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

"""
tests if the webhook server is active
    first the server connection is tested with a http GET call
    sends a <WebhookRequest> to <serverURL>, receives a <WebhookResponse>
    checks if class instances were assigned correctly and whether the session IDs (request.session & response.session)
    match
"""

import os
from json import JSONDecodeError
from typing import (
    Any,
)

import pytest
import requests
from loguru import logger

from ondewo_nlu_webhook_server.server.base_models import (
    WebhookRequest,
    WebhookResponse,
)


class TestWebhookServerE2e:
    """E2E test fixture for the webhook server."""

    server_url: str = f"http://172.17.0.1:{os.getenv('ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SERVER_PORT')}"

    def test_server_connection(
        self,
        webhook_server_for_testing: None,
        headers: dict[str, str],
    ) -> None:
        """Send a HTTP GET message to the server_url to check if it is online."""
        try:
            reply: requests.Response = requests.get(self.server_url, verify=False, headers=headers, timeout=30)
            assert reply.status_code == 200
        except requests.exceptions.ConnectionError:
            pytest.fail("Could not connect to server.")

    @pytest.mark.parametrize("server_function", ["slot_filling", "response_refinement"])
    def test_custom_code(
        self,
        server_function: str,
        webhook_server_for_testing: None,
        headers: dict[str, str],
    ) -> None:
        """Test custom code implementations slot_filling() and response_refinement()."""
        request: WebhookRequest = WebhookRequest.create_sample_request()
        if request.headers:
            headers.update(request.headers)

        request.headers = headers

        assert WebhookRequest.model_validate(request)

        self.send_request_and_validate(
            headers=headers,
            request=request,
            server_function=server_function,
            server_url=self.server_url,
        )

    @staticmethod
    def send_request_and_validate(
        request: WebhookRequest,
        server_url: str,
        server_function: str,
        headers: dict[str, str],
    ) -> WebhookResponse:
        """Send a request to the webhook server, validate the response, and return it.

        Args:
            request: The request data to be sent.
            server_url: The URL of the webhook server.
            server_function: The function to invoke ("slot_filling" or "response_refinement").
            headers: Headers to include in the request.

        Returns:
            The validated response from the webhook server.

        Raises:
            ValueError: If the response structure is invalid.
            ConnectionError: If there is an issue connecting to the webhook server.
        """
        request_url: str = f"{server_url}/{server_function}"
        logger.debug(f"Request URL: {request_url}")

        request_payload: dict[str, Any] = request.model_dump()
        logger.debug(f"Request payload: {request_payload}")

        response_obj: requests.Response
        try:
            response_obj = requests.post(
                url=request_url,
                headers=headers,
                json=request_payload,
                verify=False,
                timeout=30,
            )
            response_obj.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Error while sending request: {e}")
            raise ConnectionError(f"Failed to connect to {request_url}: {e}") from e

        assert response_obj
        response_dict: dict[str, Any]
        try:
            response_dict = response_obj.json()
            logger.debug(f"Response JSON: {response_dict}")
        except JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {response_obj.text}")
            raise ValueError(f"Invalid JSON response from server: {e}") from e

        try:
            WebhookResponse.model_validate(response_dict)
        except Exception as e:
            logger.error(f"Response validation failed: {e}")
            raise ValueError(f"Response validation failed: {e}") from e

        return WebhookResponse(**response_dict)
