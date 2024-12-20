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

FROM python:3.13-slim AS base

# Get GRPCurl
COPY --from=fullstorydev/grpcurl:latest /bin/grpcurl /usr/local/bin/

# Set timezone to Europe/Vienna
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC
ENV LANG=C.UTF-8

# set the correct docker group id in the image based on the hos
# The Docker socket on/from our host is associated with the docker group, however there is
# no guarantee that this is the same docker group in the image (the group that gets created
# by step 2’s script, and used in step 3, above). Linux groups are defined by IDs -
# so in order to align the group we set in the image with the group that exist on the host,
# they must both have the same group ID!
# HOST_DOCKER_GID := $(shell getent group docker | cut -d: -f3)
# The group ID on the host can be looked up with the command "getent group docker"
# We’ll pass it to the Docker build via an argument and then use that to modify the docker
# group ID in the image.
# See article at https://maze88.dev/docker-socket-from-within-containers.html
ARG HOST_DOCKER_GID
RUN addgroup --gid $HOST_DOCKER_GID docker  \
    && newgrp docker \
    && groupmod -g $HOST_DOCKER_GID docker \
    && newgrp docker \
    && usermod -aG docker root

# install required software packages
RUN apt update && apt upgrade -y && apt install -y \
    iputils-ping \
    gcc \
    git \
    gzip \
    make \
    p7zip \
    parallel \
    ssh \
    tar \
    tmux \
    tree \
    tzdata \
    unzip \
    vim \
    wget \
    curl \
    ffmpeg \
    rsync\
    sed \
    tmux\
    jq \
    libpq-dev \
    libreadline-dev \
    && ln -s /usr/bin/python3 /usr/bin/python \
    && curl -fsSL https://get.docker.com | sh # needed to control asterisks started as docker images \
    && apt clean  \
    && apt autoclean  \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# set the time zone to Europe/Vienna
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    dpkg-reconfigure --frontend noninteractive tzdata

RUN mkdir -p ~/.ssh && touch ~/.ssh/known_hosts && ssh-keygen -R github.com

# Set working directory.
WORKDIR /opt/ondewo-nlu-webhook-server-python

########################################################################################
# UNCYTHONIZED IMAGE
########################################################################################
FROM base AS uncythonized

ARG CACHEBUST=1

# Install requirements
COPY ./requirements.txt .
COPY ./requirements-ondewo-clients.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy source code
COPY ./ondewo_nlu_webhook_server ./ondewo_nlu_webhook_server
COPY ./ondewo_nlu_webhook_server_custom_integration ./ondewo_nlu_webhook_server_custom_integration
COPY ./RELEASE.md .
COPY ./README.md .
COPY ./LICENSE.md .
COPY ./setup.cfg .
COPY ./setup.py  .

# Generate and add LIBRARIES.md
RUN rm -f LIBRARIES.md && pip-licenses --from=mixed --with-system >> LIBRARIES.md

# Set the PYTHONPATH environment variable globally for the container
ENV PYTHONPATH=.:..

# Start server.
CMD ["python3", "ondewo_nlu_webhook_server/server/server.py"]

# Instantiate health check
EXPOSE "$ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SERVER_PORT"
HEALTHCHECK --interval=1m --timeout=5s --retries=3 \
  CMD curl -f http://localhost:${ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SERVER_PORT}/health || exit 1

########################################################################################
# CYTHONIZED IMAGE
########################################################################################
FROM base AS cythonized

# Install build dependencies
RUN pip install --upgrade pip && pip install cython setuptools wheel

# Copy source code for compilation
COPY ./ondewo_nlu_webhook_server ./ondewo_nlu_webhook_server
COPY ./ondewo_nlu_webhook_server_custom_integration ./ondewo_nlu_webhook_server_custom_integration
COPY ./requirements.txt .
COPY ./requirements-ondewo-clients.txt .
COPY ./RELEASE.md .
COPY ./README.md .
COPY ./LICENSE.md .
COPY ./setup.cfg .
COPY ./setup.py  .

# Install dependencies for building
RUN pip install -r requirements.txt

# Compile Python files to shared objects (.so)
RUN python setup.py build_ext --inplace

# Remove unnecessary Python source files to minimize image size
RUN find ./ondewo_nlu_webhook_server -name "*.py" -delete && \
    find ./ondewo_nlu_webhook_server_custom_integration -name "*.py" -delete

# Set the PYTHONPATH environment variable globally for the container
ENV PYTHONPATH=.:..

CMD ["python3", "ondewo_nlu_webhook_server/server/server.py"]

EXPOSE "$ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SERVER_PORT"
HEALTHCHECK --interval=1m --timeout=5s --retries=3 \
  CMD curl -f http://localhost:${ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SERVER_PORT}/health || exit 1
