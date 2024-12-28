# Use the official Python 3.13 image as a base
FROM python:3.13-slim

# Set timezone to Europe/Vienna
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC
ENV LANG=C.UTF-8

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
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
    && ln -s /usr/bin/python3 /usr/bin/python \
    && curl -fsSL https://get.docker.com | sh # needed to control asterisks started as docker images \
    && apt clean  \
    && apt autoclean

# set the time zone to Europe/Vienna
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    dpkg-reconfigure --frontend noninteractive tzdata

RUN mkdir -p ~/.ssh && touch ~/.ssh/known_hosts && ssh-keygen -R github.com

# Set up the working directory
WORKDIR /workspace

# Install additional Python packages globally if needed
RUN pip install --upgrade pip

# Install Python packages required for development
COPY ./requirements-ci-cd.txt .
COPY ./requirements-dev.txt  .
COPY ./requirements-ondewo-clients.txt .
COPY ./requirements-static-code-checks.txt .
COPY ./requirements.txt .
RUN make setup_developer_environment_locally

# Ensure vscode user has the correct permissions
RUN useradd -ms /bin/bash vscode
USER vscode
