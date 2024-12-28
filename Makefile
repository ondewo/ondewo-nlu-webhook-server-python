#!/usr/bin/make
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

SHELL=/bin/sh

# Set MAKEFLAGS to include the silent option
MAKEFLAGS += --silent
CONFIGS_PATH:=$(shell pwd)/configs

RELEASE_VERSION=$(shell cat ondewo_nlu_webhook_server/version.py | grep "__version__" | sed "s:__version__ = '::"  | sed "s:'::")

PYPI_USERNAME?=ENTER_HERE_YOUR_PYPI_USERNAME
PYPI_PASSWORD?=ENTER_HERE_YOUR_PYPI_PASSWORD

# You need to setup an access token at https://github.com/settings/tokens - permissions are important
GITHUB_GH_TOKEN?=ENTER_YOUR_TOKEN_HERE

CURRENT_RELEASE_NOTES=`cat RELEASE.md \
	| sed -n '/Release ONDEWO NLU Webhook Server Python ${RELEASE_VERSION}/,/\*\*/p'`

GH_REPO="https://github.com/ondewo/ondewo-nlu-webhook-server-python"
DEVOPS_ACCOUNT_GIT="ondewo-devops-accounts"
DEVOPS_ACCOUNT_DIR="./${DEVOPS_ACCOUNT_GIT}"
OUTPUT_DIR=.
IMAGE_UTILS_NAME=ondewo-nlu-webhook-server-python-utils-python:${RELEASE_VERSION}
.DEFAULT_GOAL := help

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
#       ONDEWO Standard Make Targets
########################################################

help: show_welcome ## print usage info about help targets
	# ----------------------------------------------------------------------------------
	# ONDEWO NLU Webhook Server Python - Available commands:
	# ----------------------------------------------------------------------------------
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	# ----------------------------------------------------------------------------------

makefile_chapters: ## Shows all sections of Makefile
	@echo `cat Makefile| grep "########################################################" -A 1 | grep -v "########################################################"`

show_welcome: ## Show ONDEWO Call Center AI (CCAI) Platform welcome message
	@echo ""
	@echo "#####################################################"
	@echo "# Welcome to ONDEWO NLU Webhook Server Python ${RELEASE_VERSION}"
	@echo "#####################################################"

TEST: ## Prints some important variables
	@echo "Release Notes: \n \n$(CURRENT_RELEASE_NOTES)"
	@echo "GH Token: \t $(GITHUB_GH_TOKEN)"
	@echo "NPM Name: \t $(NPM_USERNAME)"
	@echo "NPM Password: \t $(NPM_PASSWORD)"

setup_developer_environment_locally: show_welcome install_apt install_submodules install_dependencies_locally install_precommit_hooks copy_docker_config ## Sets the full environment to develop locally

setup_developer_environment_in_devcontainer: show_welcome install_submodules install_dependencies_locally install_precommit_hooks ## Sets the full environment to develop in a devcontainer

install_dependencies_locally: ## Install dependencies locally
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

install_precommit_hooks: ## Installs pre-commit hooks and sets them up for the ondewo-csi-client repo
	-pip install pre-commit
	-@if command -v conda > /dev/null 2>&1; then \
		conda -y install pre-commit; \
	else \
		echo "Conda not found, skipping conda pre-commit hook setup."; \
	fi
	pre-commit install
	pre-commit install --hook-type commit-msg

precommit_hooks_run_all_files: ## Runs all pre-commit hooks on all files and not just the changed ones
	-pre-commit run --all-file
	pre-commit run --all-file

copy_docker_config: ## Copies the users docker config to the project
	mkdir -p .docker
	cp -R ~/.docker/config.json .docker/config.json

run_code_checks: ## Build code checks image and run
	docker build -t ${IMAGE_TAG_CODE_CHECK} -f dockerfiles/code_checks/static-code-checks.Dockerfile .
	docker run --rm ${IMAGE_TAG_CODE_CHECK} make flake8
	docker run --rm ${IMAGE_TAG_CODE_CHECK} make mypy

static_code_check_image:
	DOCKER_BUILDKIT=1 docker build \
		-t ${IMAGE_CODE_TEST} \
		-f dockerfiles/code_checks/static-code-checks.Dockerfile \
		--build-arg CACHEBUST=$$(date +%s) \
		.

mypy: ## Run mypy static code checking
	@echo "---------------------------------------------"
	@echo "START: Run mypy in pre-commit hook ..."
	pre-commit run mypy --all-files
	@echo "DONE: Run mypy in pre-commit hook."
	@echo "---------------------------------------------"
	@echo "START: Run mypy directly ..."
	mypy --config-file=dockerfiles/code_checks/mypy.ini .
	@echo "DONE: Run mypy directly"
	@echo "---------------------------------------------"

mypy_in_docker: ## execute mypy in the static_code_check_image
	make static_code_check_image IMAGE_CODE_TEST=ondewo-cai-code-test:local
	docker run --rm ondewo-cai-code-test:local make mypy

flake8: ## Runs flake8
	flake8 --config dockerfiles/code_checks/.flake8 .

flake8_in_docker: ## execute mypy in the static_code_check_image
	make static_code_check_image IMAGE_CODE_TEST=ondewo-nlu-webhook-server-python-code-test:local
	docker run --rm ondewo-cai-code-test:local make flake8

create_libraries_md:
	@rm -f LIBRARIES.md
	docker run \
		--rm \
		--user $(id -u):$(id -g) \
		-v ${PWD}:${ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_APP_DIR} \
		${DOCKERREGISTRY}/${NAMESPACE}/ondewo-nlu-webhook-server-python-release:${ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_VERSION} /bin/bash -c 'rm -f LIBRARIES.md && pip-licenses --from=mixed --with-system >> LIBRARIES.md'
	@echo "LIBRARIES.md file updated"

curl_docker_socket:
	# How to docker socket: https://maze88.dev/docker-socket-from-within-containers.html
	curl --unix-socket /var/run/docker.sock http://api/containers/json | jq

########################################################
#       Repo Specific Make Targets
########################################################

# for local use
build: PUSH_NAME=${PUSH_NAME_ROOT}:develop
build: clear_package_data init_submodules checkout_defined_submodule_versions build_server_image_uncythonized

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

build_server_image_release: ## Build the image
	echo "Environment set to '${ENV}'"
	git submodule update --init --recursive
	docker build \
		-t ${ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_IMAGE_NAME}-release \
 		-f dockerfiles/ondewo-nlu-webhook-server-python.Dockerfile  \
		--target cythonized \
 		--build-arg HOST_DOCKER_GID=${HOST_DOCKER_GID} \
		--build-arg HOST_DOCKER_GID=$(shell getent group docker | cut -d: -f3) \
		--build-arg CACHEBUST=$$(date +%s) \
 		.

run_ondewo_nlu_webhook_server_release_in_container: show_welcome ## RUn the server release in as a container with nginx
	@if [ ! -d "${ONDEWO_INGRESS_ENVOY_CERTS_PATH}" ]; then \
		$(MAKE) run_ondewo_nlu_webhook_server_create_ssl_certificates; \
	fi;
	docker compose -f docker-compose.yaml --env-file envs/${ENV}.env build
	docker compose -f docker-compose.yaml --env-file envs/${ENV}.env up --force-recreate --renew-anon-volumes

run_ondewo_nlu_webhook_server_release_in_container_daemon: show_welcome ## RUn the server release in as a container with nginx as daemon
	@if [ ! -d "${ONDEWO_INGRESS_ENVOY_CERTS_PATH}" ]; then \
		$(MAKE) run_ondewo_nlu_webhook_server_create_ssl_certificates; \
	fi;
	docker compose -f docker-compose.yaml --env-file envs/${ENV}.env build
	docker compose -f docker-compose.yaml --env-file envs/${ENV}.env up -d --force-recreate --renew-anon-volumes

run_ondewo_nlu_webhook_server_create_ssl_certificates: ## Creates ssl certificates
	@echo "make up: Preparing ondewo-ingress: generating ssl certificates ..."
	rm -rf ${ONDEWO_INGRESS_ENVOY_CERTS_PATH}
	mkdir -p ${ONDEWO_INGRESS_ENVOY_CERTS_PATH}

	@echo "  (1/9) Generate CA's private key and self-signed certificate ..."
	openssl req \
		-x509 \
		-newkey rsa:4096 \
		-days 365 -nodes \
		-keyout ${ONDEWO_INGRESS_ENVOY_CERTS_PATH}/ca-key.pem \
		-out ${ONDEWO_INGRESS_ENVOY_CERTS_PATH}/ca-cert.pem \
		-subj "/C=${ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SSL_CERT_COUNTRY_CODE}/ST=${ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SSL_CERT_STATE}/L=${ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SSL_CERT_LOCALITY}/O=${ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SSL_CERT_ORGANISATION}/OU=${ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SSL_CERT_ORGANISATION_UNIT} Certificate Authority/CN=${ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SSL_CERT_COMMON_NAME}/emailAddress=${ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SSL_CERT_E_MAIL}" \
		> "/dev/null"
	@echo "  ✔️ (1/9) Generate CA's private key and self-signed certificate"

	@echo "  (2/9) CA's self-signed certificate ..."
	openssl x509 -in ${ONDEWO_INGRESS_ENVOY_CERTS_PATH}/ca-cert.pem -noout -text > "/dev/null"
	@echo "  ✔️ (2/9) CA's self-signed certificate ..."

	@echo "  (3/9) Generate web server's private key and certificate signing request (CSR) ..."
	openssl req \
		-newkey rsa:4096 \
		-nodes \
		-keyout ${ONDEWO_INGRESS_ENVOY_CERTS_PATH}/server-key.pem \
		-out ${ONDEWO_INGRESS_ENVOY_CERTS_PATH}/server-req.pem \
		-subj "/C=${ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SSL_CERT_COUNTRY_CODE}/ST=${ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SSL_CERT_STATE}/L=${ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SSL_CERT_LOCALITY}/O=${ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SSL_CERT_ORGANISATION}/OU=${ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SSL_CERT_ORGANISATION_UNIT} Certificate Authority/CN=${ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SSL_CERT_COMMON_NAME}/emailAddress=${ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SSL_CERT_E_MAIL}" \
		> "/dev/null"
	@echo "  ✔️ (3/9) Generate web server's private key and certificate signing request (CSR)"

	# Remember that when we develop on localhost, It’s important to add the IP:0.0.0.0 as an Subject Alternative Name (SAN) extension to the certificate.
	@echo "subjectAltName=DNS:*.tls,DNS:localhost,IP:0.0.0.0" > ${ONDEWO_INGRESS_ENVOY_CERTS_PATH}/server-ext.cnf
	# Or you can use localhost DNS and grpc.ssl_target_name_override variable
	# echo "subjectAltName=DNS:localhost" > server-ext.cnf

	@echo "  (4/9) Use CA's private key to sign web server's CSR and get back the signed certificate ..."
	openssl x509 -req \
		-in ${ONDEWO_INGRESS_ENVOY_CERTS_PATH}/server-req.pem \
		-days 365 \
		-CA ${ONDEWO_INGRESS_ENVOY_CERTS_PATH}/ca-cert.pem \
		-CAkey ${ONDEWO_INGRESS_ENVOY_CERTS_PATH}/ca-key.pem \
		-CAcreateserial \
		-out ${ONDEWO_INGRESS_ENVOY_CERTS_PATH}/server-cert.pem \
		-extfile ${ONDEWO_INGRESS_ENVOY_CERTS_PATH}/server-ext.cnf \
		> "/dev/null"
	@echo "  ✔️ (4/9) Use CA's private key to sign web server's CSR and get back the signed certificate"

	@echo "  (5/9) Server's signed certificate ..."
	openssl x509 \
		-in ${ONDEWO_INGRESS_ENVOY_CERTS_PATH}/server-cert.pem \
		-noout \
		-text \
		> "/dev/null"
	@echo "  ✔️ (5/9) Server's signed certificate"

	@echo "  (6/9) Generate client's private key and certificate signing request (CSR) ..."
	openssl req \
		-newkey rsa:4096 \
		-nodes \
		-keyout ${ONDEWO_INGRESS_ENVOY_CERTS_PATH}/client-key.pem \
		-out ${ONDEWO_INGRESS_ENVOY_CERTS_PATH}/client-req.pem \
		-subj "/C=${ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SSL_CERT_COUNTRY_CODE}/ST=${ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SSL_CERT_STATE}/L=${ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SSL_CERT_LOCALITY}/O=${ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SSL_CERT_ORGANISATION}/OU=${ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SSL_CERT_ORGANISATION_UNIT} Certificate Authority/CN=${ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SSL_CERT_COMMON_NAME}/emailAddress=${ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SSL_CERT_E_MAIL}" \
		> "/dev/null"
	@echo "  ✔️ (6/9) Generate client's private key and certificate signing request (CSR)"

	# Remember that when we develop on localhost, It’s important to add the IP:0.0.0.0 as an Subject Alternative Name (SAN) extension to the certificate.
	@echo "subjectAltName=DNS:*.client.com,IP:0.0.0.0" > ${ONDEWO_INGRESS_ENVOY_CERTS_PATH}/client-ext.cnf

	@echo "  (7/9) Use CA's private key to sign client's CSR and get back the signed certificate ..."
	openssl x509 -req \
		-in ${ONDEWO_INGRESS_ENVOY_CERTS_PATH}/client-req.pem \
		-days 60 \
		-CA ${ONDEWO_INGRESS_ENVOY_CERTS_PATH}/ca-cert.pem \
		-CAkey ${ONDEWO_INGRESS_ENVOY_CERTS_PATH}/ca-key.pem \
		-CAcreateserial -out ${ONDEWO_INGRESS_ENVOY_CERTS_PATH}/client-cert.pem \
		-extfile ${ONDEWO_INGRESS_ENVOY_CERTS_PATH}/client-ext.cnf \
		> "/dev/null"
	@echo "  ✔️ (7/9) Use CA's private key to sign client's CSR and get back the signed certificate"

	@echo "  (8/9) Client's signed certificate ..."
	openssl x509 -in ${ONDEWO_INGRESS_ENVOY_CERTS_PATH}/client-cert.pem -noout -text > "/dev/null"
	@echo "  ✔️ (8/9) Client's signed certificate"

	@echo "  (9/9) Setting correct permissions for certificates ..."
	chmod go+r ${ONDEWO_INGRESS_ENVOY_CERTS_PATH} -R
	@echo "  ✔️ (9/9) Setting correct permissions for certificates ..."
	@echo "✔️ make up: Preparing ondewo-ingress-envoy: generating ssl certificates"

########################################################
#		Release

release: ## Automate the entire release process
	@echo "Start Release"
	make build
	/bin/bash -c 'source `conda info --base`/bin/activate ondewo-nlu-webhook-server-python; make precommit_hooks_run_all_files || echo "PRECOMMIT FOUND SOMETHING"'
	git status
	git add ondewo
	git add Makefile
	git add RELEASE.md
	git add setup.py
	git add ondewo_nlu_webhook_server
	git add ondewo_nlu_webhook_server_custom_integration
	git status
	-git commit -m "PREPARING FOR RELEASE ${RELEASE_VERSION}"
	git push
	make create_release_branch
	make create_release_tag
	make release_to_github_via_docker
	make push_to_pypi_via_docker
	@echo "Release Finished"

create_release_branch: ## Create Release Branch and push it to origin
	git checkout -b "release/${RELEASE_VERSION}"
	git push -u origin "release/${RELEASE_VERSION}"

create_release_tag: ## Create Release Tag and push it to origin
	git tag -a ${RELEASE_VERSION} -m "release/${RELEASE_VERSION}"
	git push origin ${RELEASE_VERSION}

login_to_gh: ## Login to Github CLI with Access Token
	echo $(GITHUB_GH_TOKEN) | gh auth login -p ssh --with-token

build_gh_release: ## Generate Github Release with CLI
	gh release create --repo $(GH_REPO) "$(RELEASE_VERSION)" -n "$(CURRENT_RELEASE_NOTES)" -t "Release ${RELEASE_VERSION}"

########################################################
#		Submodules

install: init_submodules ## Installs all packages
	# pip install -e .

init_submodules:  ## Initialize submodules
	# @echo "START initializing submodules ..."
	# git submodule update --init --recursive
	# @echo "DONE initializing submodules"

checkout_defined_submodule_versions:  ## Update submodule versions
	# @echo "START checking out submodules ..."
	# git -C ${ONDEWO_SUBMODULE_DIR} fetch --all
	# git -C ${ONDEWO_SUBMODULE_DIR} checkout ${ONDEWO_SUBMODULE_GIT_BRANCH}
	# @echo "DONE checking out submodules"

########################################################
#		PYPI

build_package: ## Builds PYPI Package
	python setup.py sdist bdist_wheel
	chmod a+rw dist -R

upload_package: ## Uploads PYPI Package
	twine upload --verbose -r pypi dist/* -u${PYPI_USERNAME} -p${PYPI_PASSWORD}

clear_package_data: ## Clears PYPI Package
	echo "Waiting 5s so directory for removal is not busy anymore"
	sleep 5s
	-rm -rf build dist ondewo_nlu_client.egg-info

build_utils_docker_image:  ## Build utils docker image
	docker build -f Dockerfile.utils -t ${IMAGE_UTILS_NAME} .

push_to_pypi_via_docker_image:  ## Push source code to pypi via docker
	[ -d $(OUTPUT_DIR) ] || mkdir -p $(OUTPUT_DIR)
	docker run --rm \
		-v ${shell pwd}/dist:/home/ondewo/dist \
		-e PYPI_USERNAME=${PYPI_USERNAME} \
		-e PYPI_PASSWORD=${PYPI_PASSWORD} \
		${IMAGE_UTILS_NAME} make push_to_pypi
	rm -rf dist

push_to_pypi: build_package upload_package clear_package_data ## Builds -> Uploads -> Clears PYPI Package
	@echo 'YAY - Pushed to pypi : )'

show_pypi: build_package ## Shows PYPI Package with Dockerimage
	tar xvfz dist/ondewo-nlu-webhook-server-${RELEASE_VERSION}.tar.gz
	tree ondewo-nlu-client-${RELEASE_VERSION}
	cat ondewo-nlu-client-${RELEASE_VERSION}/ondewo_nlu_client.egg-info/requires.txt

show_pypi_via_docker_image: build_utils_docker_image ## Push source code to pypi via docker
	[ -d $(OUTPUT_DIR) ] || mkdir -p $(OUTPUT_DIR)
	docker run --rm \
		-v ${shell pwd}/dist:/home/ondewo/dist \
		-e PYPI_USERNAME=${PYPI_USERNAME} \
		-e PYPI_PASSWORD=${PYPI_PASSWORD} \
		${IMAGE_UTILS_NAME} make show_pypi
	rm -rf dist

########################################################
#		GITHUB

push_to_gh: login_to_gh build_gh_release ## Logs into GitHub CLI and Releases
	@echo 'Released to Github'

release_to_github_via_docker_image:  ## Release to Github via docker
	docker run --rm \
		-e GITHUB_GH_TOKEN=${GITHUB_GH_TOKEN} \
		${IMAGE_UTILS_NAME} make push_to_gh

########################################################
#		DEVOPS-ACCOUNTS

ondewo_release: spc clone_devops_accounts run_release_with_devops ## Release with credentials from devops-accounts repo
	@rm -rf ${DEVOPS_ACCOUNT_GIT}

clone_devops_accounts: ## Clones devops-accounts repo
	if [ -d $(DEVOPS_ACCOUNT_GIT) ]; then rm -Rf $(DEVOPS_ACCOUNT_GIT); fi
	git clone git@bitbucket.org:ondewo/${DEVOPS_ACCOUNT_GIT}.git

run_release_with_devops: ## Gets Credentials from devops-repo and run release command with them
	$(eval info:= $(shell cat ${DEVOPS_ACCOUNT_DIR}/account_github.env | grep GITHUB_GH & cat ${DEVOPS_ACCOUNT_DIR}/account_pypi.env | grep PYPI_USERNAME & cat ${DEVOPS_ACCOUNT_DIR}/account_pypi.env | grep PYPI_PASSWORD))
	@(echo ${CONDA_PREFIX} | grep -q nlu-webhook-server-python || make setup_conda_env $(info)) && make release $(info)

spc: ## Checks if the Release Branch, Tag and Pypi version already exist
	$(eval filtered_branches:= $(shell git branch --all | grep "release/${RELEASE_VERSION}"))
	$(eval filtered_tags:= $(shell git tag --list | grep "${RELEASE_VERSION}"))
	@if test "$(filtered_branches)" != ""; then echo "-- Test 1: Branch exists!!" & exit 1; else echo "-- Test 1: Branch is fine";fi
	@if test "$(filtered_tags)" != ""; then echo "-- Test 2: Tag exists!!" & exit 1; else echo "-- Test 2: Tag is fine";fi
