# Use the official Python 3.13 image as a base
FROM python:3.13-slim

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
    && ln -s /usr/bin/python3 /usr/bin/python \
    && apt clean  \
    && apt autoclean

# set the time zone to Europe/Vienna
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    dpkg-reconfigure --frontend noninteractive tzdata

RUN mkdir -p ~/.ssh && touch ~/.ssh/known_hosts && ssh-keygen -R github.com

# Set up the working directory
WORKDIR /github/ondewo-nlu-webhook-server-python

# Install additional Python packages globally if needed
RUN pip install --upgrade pip

# Ensure vscode user has the correct permissions
RUN useradd -ms /bin/bash vscode
USER vscode

RUN echo 'export PATH=$PATH:/home/vscode/.local/bin' >> /home/vscode/.bashrc
