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
import json
import os
from typing import (
    Any,
    Dict,
)

import pytest
import requests

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

    server_url: str = f"http://localhost:{os.getenv('ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SERVER_PORT')}"

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
        #     request.queryResult.intent.displayName = active_intent
        request.headers = headers

        # validate request structure (testing the test)
        assert WebhookRequest.model_validate(request)

        # send it to the server, src test function (not slot_filling() and last_minute_check())
        self.send_request_and_validate(
            request=request,
            server_url=self.server_url,
            server_function=server_function,
            headers=headers,
        )

    @staticmethod
    def send_request_and_validate(
        request: WebhookRequest,
        server_url: str,
        server_function: str,
        headers: Dict[str, str],
    ) -> WebhookResponse:
        """
        send the request to the webhook server, asserts if the response has a valid structure and returns it

        Args:
            request: request sent to webhook server
            server_url: webhook server url
            server_function: either "slot_filling" or "last_minute_check"

        Returns:
            response from webhook server
        """
        # send request to webhook server
        # mixin not recognized by mypy -> type ignore
        response_obj = requests.post(
            url=server_url + "/" + server_function,
            headers=headers,
            json=request.json(),
            verify=False,
        )
        try:
            response_dict: Dict[str, Any] = response_obj.json()
            json.dumps(response_dict)
        except ValueError:
            pytest.fail("response could not be json formatted")

        # response-dictionary structure validation
        assert WebhookResponse.model_validate(response_dict)  # type:ignore

        # assign WebhookResponse dataclass
        response: WebhookResponse = WebhookResponse(**response_dict)
        return response
