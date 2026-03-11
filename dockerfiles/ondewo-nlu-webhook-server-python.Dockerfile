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

FROM python:3.14-slim AS base

# Get GRPCurl
COPY --from=fullstorydev/grpcurl:latest /bin/grpcurl /usr/local/bin/

# Set timezone and locale
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=UTC \
    LANG=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the correct docker group id based on the host
ARG HOST_DOCKER_GID
RUN addgroup --gid $HOST_DOCKER_GID docker  \
    && newgrp docker \
    && groupmod -g $HOST_DOCKER_GID docker \
    && newgrp docker \
    && usermod -aG docker root

# Install required system packages in a single layer and clean up
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
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
    rsync \
    sed \
    jq \
    libpq-dev \
    libreadline-dev \
    && curl -fsSL https://get.docker.com | sh \
    && ln -s /usr/bin/python3 /usr/bin/python \
    && apt-get clean \
    && apt-get autoclean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Set the time zone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    dpkg-reconfigure --frontend noninteractive tzdata

RUN mkdir -p ~/.ssh && touch ~/.ssh/known_hosts && ssh-keygen -R github.com

# Set working directory
WORKDIR /opt/ondewo-nlu-webhook-server-python

# Copy uv binary from official uv Docker image (shared across stages)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

########################################################################################
# UNCYTHONIZED IMAGE
########################################################################################
FROM base AS uncythonized

ARG CACHEBUST=1

# Copy project files (source must be present before install for dynamic version resolution)
COPY ./pyproject.toml ./setup.cfg ./setup.py ./
COPY ./ondewo_nlu_webhook_server ./ondewo_nlu_webhook_server
COPY ./ondewo_nlu_webhook_server_custom_integration ./ondewo_nlu_webhook_server_custom_integration
COPY ./RELEASE.md ./README.md ./LICENSE.md ./

# Install dependencies
RUN uv pip install --system -e .

# Generate and add LIBRARIES.md
RUN rm -f LIBRARIES.md && pip-licenses --from=mixed --with-system >> LIBRARIES.md

# Create non-root user for production security
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

# Start server
CMD ["python3", "-m", "ondewo_nlu_webhook_server.server"]

EXPOSE "$ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SERVER_PORT"
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:${ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SERVER_PORT}/health || exit 1

########################################################################################
# CYTHONIZED IMAGE
########################################################################################
FROM base AS cythonized

# Install build dependencies
RUN uv pip install --system cython setuptools wheel

# Copy all project files (setup.py needs source files for cythonize)
COPY ./pyproject.toml ./setup.cfg ./setup.py ./
COPY ./ondewo_nlu_webhook_server ./ondewo_nlu_webhook_server
COPY ./ondewo_nlu_webhook_server_custom_integration ./ondewo_nlu_webhook_server_custom_integration
COPY ./RELEASE.md ./README.md ./LICENSE.md ./

# Install runtime dependencies only (--no-build-isolation to avoid triggering setup.py compilation)
RUN uv pip install --system --no-build-isolation -e .

# Compile Python files to shared objects (.so) with Cython
RUN python setup.py build_ext --inplace

# Remove unnecessary python source files and C artifacts to minimize image size
# Keep __init__.py and __main__.py (needed for 'python -m' execution)
RUN find ./ondewo_nlu_webhook_server ./ondewo_nlu_webhook_server_custom_integration -type f \( \
    \( -name "*.py" ! -name "__init__.py" ! -name "__main__.py" \) \
    -o -name "*.c" \
    \) -delete

# Create non-root user for production security
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

CMD ["python3", "-m", "ondewo_nlu_webhook_server.server"]

EXPOSE "$ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SERVER_PORT"
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:${ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SERVER_PORT}/health || exit 1