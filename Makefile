# Copyright 2021-2025 ONDEWO GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/usr/bin/make
SHELL = /bin/sh
RELEASE_VERSION=$(shell cat ondewo_nlu_webhook_server/version.py | sed "s:__version__ = '::"  | sed "s:'::")

TESTFILE := ondewo_nlu_webhook_server
IMAGE_TAG_CODE_CHECK := code_check_image_${TESTFILE}
PUSH_NAME_ROOT := registry-dev.ondewo.com:5000/ondewo/ondewo-nlu-webhook-server-python
PUSH_NAME_ROOT_QUAY := registry.ondewo.com:5000/ondewo/ondewo-nlu-webhook-server-python
ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_CONTAINER_NAME := ondewo-nlu-webhook-server-python

HOST_DOCKER_GID := $(shell getent group docker | cut -d: -f3)

ENV ?= local
-include envs/${ENV}.env
export

########################################################
# --- Setup developer environment                  --- #
########################################################

help: ## print usage info about help targets
	# ----------------------------------------------------------------------------------
	# ONDEWO NLU Webhook Server Python - Available commands:
	# ----------------------------------------------------------------------------------
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	# ----------------------------------------------------------------------------------

makefile_chapters: ## Shows all sections of Makefile
	@echo `cat Makefile| grep "########################################################" -A 1 | grep -v "########################################################"`

setup_developer_environment_locally: install_apt install_submodules install_precommit_hooks install_dependencies_locally ## Sets the full environment to develop locally

install_dependencies_locally: ## install local dependencies
	pip install -r requirements-dev.txt

install_submodules:
	echo "No submodules needed"
	#	git submodule update --init --recursive
	#	pip install --no-cache-dir -e ondewo-utils
	#	echo submodule ondewo-utils installed!

install_apt:
	sudo apt update && sudo apt install -y \
		libpq-dev \
		libreadline-dev \
		tree \
		tmux\
		vim \
		curl\
		sed \
		wget\
		parallel

install_precommit_hooks: ## Installs pre-commit hooks and sets them up for the ondewo-s2t repo
	pip install pre-commit
	conda install -y pre-commit
	pre-commit install
	pre-commit install --hook-type commit-msg

precommit_hooks_run_all_files: ## Runs all pre-commit hooks on all files and not just the changed ones
	pre-commit run --all-files

run_code_checks: ## Build code checks image and run
	docker build -t ${IMAGE_TAG_CODE_CHECK} -f dockerfiles/code_checks/static-code-checks.Dockerfile .
	docker run --rm ${IMAGE_TAG_CODE_CHECK} make flake8
	docker run --rm ${IMAGE_TAG_CODE_CHECK} make mypy

flake8: ## perform flake8 style checks according to .flake8
	flake8 --config dockerfiles/code_checks/.flake8 \
		ondewo_nlu_webhook_server \
		ondewo_nlu_webhook_server_custom_integration \
		tests

static_code_check_image:
	DOCKER_BUILDKIT=1 docker build \
		-t ${IMAGE_CODE_TEST} \
		-f dockerfiles/code_checks/static-code-checks.Dockerfile \
		--build-arg CACHEBUST=$$(date +%s) \
		.

mypy: ## perform mypy type checks on the project as configured in mypy.ini
	mypy --config-file dockerfiles/code_checks/mypy.ini --show-error-codes \
		ondewo_nlu_webhook_server \
		ondewo_nlu_webhook_server_custom_integration \
		tests

mypy_in_docker: ## execute mypy in the static_code_check_image
	make static_code_check_image IMAGE_CODE_TEST=ondewo-cai-code-test:local
	docker run --rm ondewo-cai-code-test:local make mypy

flake8_in_docker: ## execute mypy in the static_code_check_image
	make static_code_check_image IMAGE_CODE_TEST=ondewo-cai-code-test:local
	docker run --rm ondewo-cai-code-test:local make flake8

create_libraries_md:
	@rm -f LIBRARIES.md
	docker run --rm --user $(id -u):$(id -g) -v ${PWD}:${ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_APP_DIR} ${DOCKERREGISTRY}/${NAMESPACE}/ondewo-nlu-webhook-server-python-release:${ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_IMAGE_TAG} /bin/bash -c 'rm -f LIBRARIES.md && pip-licenses --from=mixed --with-system >> LIBRARIES.md'
	@echo "LIBRARIES.md file updated"

curl_docker_socket:
	# How to docker socket: https://maze88.dev/docker-socket-from-within-containers.html
	curl --unix-socket /var/run/docker.sock http://api/containers/json | jq

########################################################
# --- build and run                           --- #
########################################################
# for local use
build: PUSH_NAME=${PUSH_NAME_ROOT}:develop
build: build_server_image_uncythonized

build_server_image: build_server_image_uncythonized ## Build the image

build_server_image_uncythonized: ## Build the image
	echo "Environment set to '${ENV}'"
	git submodule update --init --recursive
	docker build \
		-t ${ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_IMAGE_NAME} \
 		-f dockerfiles/ondewo-nlu-webhook-server-python.Dockerfile  \
		--target uncythonized \
 		--build-arg HOST_DOCKER_GID=${HOST_DOCKER_GID} \
		--build-arg HOST_DOCKER_GID=$(shell getent group docker | cut -d: -f3) \
		--build-arg CACHEBUST=$$(date +%s) \
 		.

run_ondewo_nlu_webhook_server_in_container:
	docker compose -f docker-compose.yaml --env-file envs/${ENV}.env build
	docker compose -f docker-compose.yaml --env-file envs/${ENV}.env up --force-recreate --renew-anon-volumes

run_ondewo_nlu_webhook_server_in_container_daemon:
	docker compose -f docker-compose.yaml --env-file envs/${ENV}.env build
	docker compose -f docker-compose.yaml --env-file envs/${ENV}.env up -d --force-recreate --renew-anon-volumes



########################################################
# --- Release                                      --- #
########################################################

ondewo_release: spc create_release_branch create_release_tag ## Release and docker push

create_release_branch: ## Create Release Branch and push it to origin
# check if the branch does not exists and if it exists, delete it
	@if git show-ref --verify --quiet "refs/heads/release/${RELEASE_VERSION}"; then \
        git checkout master; \
		git branch -D "release/${RELEASE_VERSION}"; \
    fi
	git checkout -b "release/${RELEASE_VERSION}"
	git push -u origin "release/${RELEASE_VERSION}"

create_release_tag: ## Create Release Tag and push it to origin
# check if the tag does not exists and if it exists, delete it
	@if git rev-parse -q --verify "refs/tags/$(RELEASE_VERSION)"; then \
        git tag -d $(RELEASE_VERSION); \
		git push origin ":refs/tags/$(RELEASE_VERSION)"; \
    fi
	git tag -a ${RELEASE_VERSION} -m "release/${RELEASE_VERSION}"
	git push origin ${RELEASE_VERSION}

spc: ## Checks if the Release Branch, Tag and Pypi version already exist
	$(eval filtered_branches:= $(shell git branch --all | grep "release/${RELEASE_VERSION}"))
	@if test "$(filtered_branches)" != ""; then \
		echo "-- Test 1: Branch 'release/${RELEASE_VERSION}' exists!!"; \
		read -p "Overwrite the branch? (y/n): " input; \
		if [ "$$input" = "y" ]; then \
			echo "Overwriting Branch 'release/${RELEASE_VERSION}'"; \
		else \
			echo "Branch creation aborted"; \
			exit 1; \
		fi \
	else \
		echo "-- Test 1: Branch 'release/${RELEASE_VERSION}' is free to use"; \
	fi
	$(eval filtered_tags:= $(shell git tag --list | grep "${RELEASE_VERSION}"))
	@if test "$(filtered_tags)" != ""; then \
		echo "-- Test 2: Tag '${RELEASE_VERSION}' exists!!"; \
		read -p "Overwrite the tag? (y/n): " input; \
		if [ "$$input" = "y" ]; then \
			echo "Overwriting tag '${RELEASE_VERSION}'"; \
		else \
			echo "Tag creation aborted!"; \
			exit 1; \
		fi \
	else \
		echo "-- Test 2: Tag '${RELEASE_VERSION}' is free to use"; \
	fi
