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
    Dict,
)

import pytest
import requests
from ondewo.logging.logger import logger_console as log

from ondewo_nlu_webhook_server.server.base_models import (
    WebhookRequest,
    WebhookResponse,
)


class TestWebhookServerE2e:
    """
    A test fixture is provided that containerizes the current implementation via the Dockerfile in the root directory
    There are 3 tests defined that can be run for arbitrary implementations in CUSTOM_CODE.py:
    - connection test, to see if the server is running
    - test custom code: slot filling - validates the output of the slot_filling()-function in CUSTOM_CODE.py
    - test custom code: response refinement - validates the output of the response_refinement()-function in
        CUSTOM_CODE.py
    """

    server_url: str = f"http://172.17.0.1:{os.getenv('ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SERVER_PORT')}"

    def test_server_connection(
        self,
        webhook_server_for_testing: None,
        headers: Dict[str, str],
    ) -> None:
        """
        Sends a http GET message to the server_url base directory to see if it is online
        checks the welcome message on the frontpage
        fails upon ConnectionError (requests package) or if welcome message is missing

        Args:
            webhook_server_for_testing: test fixture for dockerized container
        """

        # tests connection
        try:
            reply = requests.get(self.server_url, verify=False, headers=headers)
            assert reply.status_code == 200
        except requests.exceptions.ConnectionError:
            pytest.fail("Could not connect to server.")

    @pytest.mark.parametrize("server_function", ["slot_filling", "response_refinement"])
    def test_custom_code(
        self,
        server_function: str,
        webhook_server_for_testing: None,
        headers: Dict[str, str],
    ) -> None:
        """
        Tests the custom code implementations slot_filling() and response_refinement() by sending a request without a
            special header to the webhook server for all active intents listed in CUSTOM_CODE.py. The received
            response is validated.

        Args:
            webhook_server_for_testing: test fixture for dockerized container
            server_function: either "slot_filling" or "response_refinement"
        """
        # for active_intent in active_intents:
        request: WebhookRequest = WebhookRequest.create_sample_request()
        # update headers with request headers if exists
        if request.headers:
            headers.update(request.headers)

        # assign headers to request
        request.headers = headers

        # validate request structure (testing the test)
        assert WebhookRequest.model_validate(request)

        # send it to the server, src test function (not slot_filling() and last_minute_check())
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
        headers: Dict[str, str],
    ) -> WebhookResponse:
        """
        Sends a request to the webhook server, validates the response structure, and returns it.

        Args:
            request (WebhookRequest):
                The request data to be sent to the webhook server.
            server_url (str):
                The URL of the webhook server.
            server_function (str):
                The function to be invoked on the server, typically "slot_filling" or "last_minute_check".
            headers (Dict[str, str]):
                A dictionary containing headers to be included in the request.

        Returns:
            WebhookResponse: The validated response from the webhook server.

        Raises:
            ValueError: If the response structure is invalid.
            ConnectionError: If there is an issue connecting to the webhook server.
        """
        # Construct the full request URL
        request_url: str = f"{server_url}/{server_function}"
        log.debug(f"Request URL: {request_url}")

        # Serialize the request data
        request_payload: Dict[str, Any] = request.model_dump()
        log.debug(f"Request payload: {request_payload}")

        response_obj: requests.Response
        try:
            # Send the POST request
            response_obj = requests.post(
                url=request_url,
                headers=headers,
                json=request_payload,
                verify=False,
            )
            response_obj.raise_for_status()
        except requests.RequestException as e:
            log.error(f"Error while sending request: {e}")
            raise ConnectionError(f"Failed to connect to {request_url}: {e}") from e

        assert response_obj
        response_dict: Dict[str, Any]
        # Parse the response as JSON
        try:
            response_dict = response_obj.json()
            log.debug(f"Response JSON: {response_dict}")
        except JSONDecodeError as e:
            log.error(f"Invalid JSON response: {response_obj.text}")
            raise ValueError(f"Invalid JSON response from server: {e}") from e

        # Validate the response structure
        try:
            WebhookResponse.model_validate(response_dict)
        except Exception as e:
            log.error(f"Response validation failed: {e}")
            raise ValueError(f"Response validation failed: {e}") from e

        # Return the response as a WebhookResponse instance
        return WebhookResponse(**response_dict)
