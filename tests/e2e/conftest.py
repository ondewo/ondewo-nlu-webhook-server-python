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
from typing import (
    Any,
    Dict,
    Generator,
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
from ondewo.logging.logger import logger_console as log

# Container and image tag constants
CONTAINER_TAG: str = os.getenv("ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_IMAGE_NAME", "")
assert CONTAINER_TAG
CONTAINER_NAME: str = os.getenv("ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_CONTAINER_NAME", "")
assert CONTAINER_NAME
# The image ID should match the tag used for building
IMAGE_TAG: str = CONTAINER_TAG  # This should match the tag set when building the image
assert IMAGE_TAG


class CustomDockerClient(APIClient):
    """
    Wrapper to get the health check status of a given Docker container with a 'nice' function.
    """

    def __init__(
        self,
        container: Container,
        *args: Any, **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self.container_id = container.id

    def get_health_status(self) -> str:
        """
        Read the health status of the container.
        """
        return str(self.inspect_container(self.container_id)['State']['Health']['Status'])

    def check_health(self) -> bool:
        """
        Checks whether the container's health status is 'healthy'.
        """
        return self.get_health_status() == "healthy"


@pytest.fixture(scope="session")
def webhook_server_for_testing() -> Generator:
    """
    Builds and deploys a Docker container with the webhook server.
    Checks if the server is running and healthy, then yields to the test.
    After completion, the container and images are stopped and deleted.
    """
    # Initialize Docker client
    docker_client = from_env()

    # Remove the container image if exists
    log.debug("Clean up existing docker container...")
    container: Container
    try:
        container = docker_client.containers.get(CONTAINER_NAME)
        container.remove(force=True)  # force=True if you want to remove a running container
        log.debug(f"Container {CONTAINER_NAME} has been removed.")
    except NotFound:
        log.debug(f"Container {CONTAINER_NAME} not found.")
    except APIError as e:
        log.debug(f"Error removing container {CONTAINER_NAME}: {e}")

    # Build the container image
    log.debug("Building Docker image...")
    image: Image
    image, build_logs = docker_client.images.build(
        # Adjust the path to where the Dockerfile is located
        path=".",
        dockerfile="dockerfiles/ondewo-nlu-webhook-server-python.Dockerfile",
        rm=True,
        forcerm=True,
        tag=IMAGE_TAG,  # Correctly use image_tag here
        buildargs={"HOST_DOCKER_GID": os.getenv("HOST_DOCKER_GID")},
    )

    # Deploy the container with ports mapped
    log.debug("Deploying Docker container...")
    webhook_server_port: int = int(os.getenv('ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SERVER_PORT', ""))
    container = docker_client.containers.run(
        image=image.id,  # Use the image ID returned after building
        ports={f"{webhook_server_port}/tcp": webhook_server_port},
        detach=True,
        name=CONTAINER_NAME,
        # auto_remove=True,
        environment={**os.environ},
    )
    time.sleep(5)

    # Check if the container is running
    while docker_client.containers.get(CONTAINER_NAME).status != "running":
        container.reload()
        time.sleep(20)

    # Check if the container's health status is 'healthy'
    custom_docker_client: CustomDockerClient = CustomDockerClient(container=container)
    while not custom_docker_client.check_health():
        log.debug("Waiting for the server to become healthy...")
        time.sleep(5)

    # Yield to the test after the container is up and healthy
    yield

    # Cleanup: Stop the container and remove the image
    log.debug("Stopping and cleaning up the container...")
    container.stop()
    container.remove()

    # Optionally, remove the image
    log.debug(f"Removing Docker image: {IMAGE_TAG}")
    docker_client.images.remove(IMAGE_TAG)


@pytest.fixture
def headers() -> Dict[str, str]:
    # Get username and password from environment
    username: str = os.getenv("ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_HTTP_BASIC_AUTH_USERNAME", "")
    password: str = os.getenv("ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_HTTP_BASIC_AUTH_PASSWORD", "")

    # Create the HTTP Basic Auth header
    credentials: str = f"{username}:{password}"
    encoded_credentials: str = b64encode(credentials.encode('utf-8')).decode('utf-8')

    # Return headers including the Basic Auth header
    return {"Authorization": f"Basic {encoded_credentials}"}
