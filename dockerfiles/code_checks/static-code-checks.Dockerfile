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

FROM python:3.13-slim as code_checks

# Install some useful apps in the image.
RUN apt update && apt upgrade -y && apt install -y \
    bash \
    curl\
    make \
    parallel \
    sed \
    tmux\
    tree \
    vim \
    wget \
    && apt clean  \
    && apt autoclean  \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY requirements-static-code-checks.txt .
COPY dockerfiles/code_checks/.flake8 .
COPY dockerfiles/code_checks/mypy.ini .
COPY dockerfiles/code_checks/Makefile .

RUN pip install -r requirements-static-code-checks.txt

RUN mkdir code_to_test

WORKDIR code_to_test

ENV FOLDER_NAME=/opt/ondewo-nlu-webhook-server-python
COPY ondewo_nlu_webhook_server $FOLDER_NAME/ondewo_nlu_webhook_server
COPY tests $FOLDER_NAME/tests

COPY dockerfiles/code_checks .
