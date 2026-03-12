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

import os
import time
from base64 import b64encode
from collections.abc import Generator
from typing import (
    Any,
)

import pytest
from docker import (
    APIClient,
    from_env,
)
from docker.errors import (
    APIError,
    NotFound,
)
from docker.models.containers import Container
from docker.models.images import Image
from loguru import logger


# Container and image tag constants
IMAGE_NAME: str = os.getenv("ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_IMAGE_NAME", "")
CONTAINER_NAME: str = os.getenv("ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_CONTAINER_NAME", "")


class CustomDockerClient(APIClient):
    """Wrapper to get the health check status of a given Docker container."""

    def __init__(
        self,
        container: Container,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.container_id: str | None = container.id

    def get_health_status(self) -> str:
        """Read the health status of the container."""
        return str(self.inspect_container(self.container_id)["State"]["Health"]["Status"])

    def check_health(self) -> bool:
        """Check whether the container's health status is 'healthy'."""
        return self.get_health_status() == "healthy"


@pytest.fixture(scope="session")
def webhook_server_for_testing() -> Generator[None]:
    """Build and deploy a Docker container with the webhook server.

    Checks if the server is running and healthy, then yields to the test.
    After completion, the container and images are stopped and deleted.
    """
    docker_client = from_env()

    # Remove the container image if exists
    logger.debug("Clean up existing docker container...")
    container: Container
    try:
        container = docker_client.containers.get(CONTAINER_NAME)
        container.remove(force=True)
        logger.debug(f"Container {CONTAINER_NAME} has been removed.")
    except NotFound:
        logger.debug(f"Container {CONTAINER_NAME} not found.")
    except APIError as e:
        logger.debug(f"Error removing container {CONTAINER_NAME}: {e}")

    # Build the container image
    logger.debug("Building Docker image...")
    image: Image
    image, _ = docker_client.images.build(
        path=".",
        dockerfile="dockerfiles/ondewo-nlu-webhook-server-python.Dockerfile",
        rm=True,
        forcerm=True,
        target="cythonized",
        tag=IMAGE_NAME,
        buildargs={"HOST_DOCKER_GID": os.getenv("HOST_DOCKER_GID")},
    )

    # Deploy the container with ports mapped
    logger.debug("Deploying Docker container...")
    webhook_server_port: int = int(os.getenv("ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SERVER_PORT", ""))
    environment: dict[str, str] = {
        key: value for key, value in os.environ.items() if key.startswith("ONDEWO_NLU_WEBHOOK_SERVER_PYTHON")
    }
    container = docker_client.containers.run(
        image=image.id,
        ports={f"{webhook_server_port}/tcp": webhook_server_port},
        detach=True,
        name=CONTAINER_NAME,
        environment=environment,
    )
    time.sleep(5)

    # Check if the container is running
    retries_running: int = 0
    while docker_client.containers.get(CONTAINER_NAME).status != "running" and retries_running < 2:
        container.reload()
        time.sleep(20)
        retries_running += 1

    # Check if the container's health status is 'healthy'
    custom_docker_client: CustomDockerClient = CustomDockerClient(container=container)
    retries_health: int = 0
    while not custom_docker_client.check_health() and retries_health < 2:
        logger.debug("Waiting for the server to become healthy...")
        time.sleep(5)
        retries_health += 1

    yield

    # Cleanup
    logger.debug("Stopping and cleaning up the container...")
    container.stop()
    container.remove()

    logger.debug(f"Removing Docker image: {IMAGE_NAME}")
    docker_client.images.remove(IMAGE_NAME)


@pytest.fixture
def headers() -> dict[str, str]:
    username: str = os.getenv("ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_HTTP_BASIC_AUTH_USERNAME", "")
    password: str = os.getenv("ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_HTTP_BASIC_AUTH_PASSWORD", "")

    credentials: str = f"{username}:{password}"
    encoded_credentials: str = b64encode(credentials.encode("utf-8")).decode("utf-8")

    return {"Authorization": f"Basic {encoded_credentials}"}
