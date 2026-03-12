# Copy uv binary from official uv Docker image
FROM ghcr.io/astral-sh/uv:latest AS uv

# Use a base image with Python 3.14
FROM python:3.14-slim AS dev_containers_target_stage

# Set default USERID to 1000 if not passed
ARG USERNAME=vscode
ARG USERID=1000

# Set environment variables
ENV USERNAME=${USERNAME}
ENV USERID=${USERID}
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC
ENV LANG=C.UTF-8
# Optimize uv for development environment
ENV UV_SYSTEM_PYTHON=1
ENV UV_CACHE_DIR=/tmp/uv-cache

# Copy uv binary from the uv image early for better caching
COPY --from=uv /uv /usr/local/bin/uv
RUN chmod +x /usr/local/bin/uv && \
  uv --version

# Verify Python 3.14 is available from base image
RUN python3.14 --version && \
  python3 --version && \
  python --version

# Install necessary dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  curl \
  ffmpeg \
  gcc \
  git \
  gzip \
  iputils-ping \
  jq \
  libpq-dev \
  libreadline-dev \
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
  && apt-get clean \
  && apt-get autoclean \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Set the time zone to UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
  echo $TZ > /etc/timezone && \
  dpkg-reconfigure --frontend noninteractive tzdata

# Set up SSH known hosts (as root before user creation)
RUN mkdir -p /root/.ssh && \
  touch /root/.ssh/known_hosts && \
  ssh-keygen -R github.com 2>/dev/null || true

# Set up the working directory
WORKDIR /github/ondewo-nlu-webhook-server-python

# Create the user with the given username and user ID, and add to the docker and sudo groups
# Handle invalid or empty USERID by defaulting to 1000
# Handle empty USERNAME by defaulting to vscode
RUN ACTUAL_UID="${USERID:-1000}"; \
  ACTUAL_USERNAME="${USERNAME:-vscode}"; \
  if [ "$ACTUAL_UID" = "-1000" ] || ! [ "$ACTUAL_UID" -ge 0 ] 2>/dev/null; then \
  ACTUAL_UID=1000; \
  fi && \
  useradd -m --uid "$ACTUAL_UID" -s /bin/bash "$ACTUAL_USERNAME" && \
  usermod -aG sudo "$ACTUAL_USERNAME" && \
  echo "$ACTUAL_USERNAME ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Set up SSH directory for the user
RUN ACTUAL_USERNAME="${USERNAME:-vscode}"; \
  if [ -z "$ACTUAL_USERNAME" ] || [ "$ACTUAL_USERNAME" = "" ]; then \
  ACTUAL_USERNAME="vscode"; \
  fi && \
  mkdir -p /home/$ACTUAL_USERNAME/.ssh && \
  chown -R $ACTUAL_USERNAME:$ACTUAL_USERNAME /home/$ACTUAL_USERNAME/.ssh && \
  chmod 700 /home/$ACTUAL_USERNAME/.ssh

# Set up user environment and PATH (as root)
RUN ACTUAL_USERNAME="${USERNAME:-vscode}"; \
  echo "export PATH=\$PATH:/home/$ACTUAL_USERNAME/.local/bin" >> /home/$ACTUAL_USERNAME/.bashrc && \
  echo "export PATH=\$PATH:/home/$ACTUAL_USERNAME/.cargo/bin" >> /home/$ACTUAL_USERNAME/.bashrc && \
  echo "export UV_SYSTEM_PYTHON=1" >> /home/$ACTUAL_USERNAME/.bashrc && \
  echo "export UV_CACHE_DIR=/tmp/uv-cache" >> /home/$ACTUAL_USERNAME/.bashrc && \
  echo "export PYTHONPATH=/github/ondewo-nlu-webhook-server-python" >> /home/$ACTUAL_USERNAME/.bashrc && \
  echo 'alias uv="uv --system"' >> /home/$ACTUAL_USERNAME/.bashrc && \
  echo "export PYTHONUNBUFFERED=1" >> /home/$ACTUAL_USERNAME/.bashrc && \
  echo "export PYTHONDONTWRITEBYTECODE=1" >> /home/$ACTUAL_USERNAME/.bashrc

# Create .venv directory for user (will be populated in postCreateCommand)
RUN ACTUAL_USERNAME="${USERNAME:-vscode}"; \
  mkdir -p /home/$ACTUAL_USERNAME/.venv && \
  chown -R $ACTUAL_USERNAME:$ACTUAL_USERNAME /home/$ACTUAL_USERNAME/.venv

# Verify Python 3.14 is installed and accessible
RUN python3.14 --version && \
  which python3.14 && \
  which python3 && \
  which python

# Switch to the non-root user
# Note: The ARG USERNAME has a default value of "vscode" when not provided via --build-arg
USER ${USERNAME}
