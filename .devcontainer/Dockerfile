# Use the official Python 3.13 image as a base
FROM python:3.13-slim

ARG HOST_DOCKER_GID=999
RUN addgroup --gid $HOST_DOCKER_GID docker && newgrp docker && groupmod -g $HOST_DOCKER_GID docker && newgrp docker && usermod -aG docker root

# Set default USERID to 1000 if not passed
ARG USERNAME
ARG USERID=1000

# Set environment variables
ENV USERNAME=${USERNAME}
ENV USERID=${USERID}

# Set timezone to Europe/Vienna
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC
ENV LANG=C.UTF-8

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    ffmpeg \
    gcc \
    git \
    gzip \
    iputils-ping \
    jq \
    make \
    p7zip \
    parallel \
    passwd \
    rsync \
    sed \
    ssh \
    sudo \
    tar \
    tmux \
    tree \
    tzdata \
    unzip \
    vim \
    wget \
    docker.io \
    && apt clean  \
    && apt autoclean

# RUN curl -fsSL https://get.docker.com | sh

# set the time zone to Europe/Vienna
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    dpkg-reconfigure --frontend noninteractive tzdata

RUN mkdir -p ~/.ssh && touch ~/.ssh/known_hosts && ssh-keygen -R github.com

# Set up the working directory
WORKDIR /github/ondewo-nlu-webhook-server-python

# Install additional Python packages globally if needed
RUN pip install --upgrade pip

# Create the user with the given username and user ID, and add to the docker group
RUN useradd -m --uid ${USERID} -s /bin/bash ${USERNAME} && \
    usermod -aG docker ${USERNAME} && usermod -aG sudo ${USERNAME}

USER $USERNAME

RUN newgrp docker

RUN echo 'export PATH=$PATH:/home/$USERNAME/.local/bin' >> /home/$USERNAME/.bashrc
