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

from typing import (
    Any,
    Dict,
)

from fastapi.testclient import TestClient

from ondewo_nlu_webhook_server.server.__main__ import app
from ondewo_nlu_webhook_server.server.base_models import WebhookResponse

client = TestClient(app)


def test_valid_request(valid_request_data: Dict[str, Any], headers: Dict[str, str]) -> None:
    """Test valid request with known call_case."""
    response = client.post(
        url="/slot_filling",
        headers=headers,
        json=valid_request_data,
    )
    assert response.status_code == 200
    response_json: Dict[str, Any] = response.json()
    assert "fulfillmentMessages" in response_json
    assert "source" in response_json
    assert "payload" in response_json
    assert "outputContexts" in response_json

    webhook_response: WebhookResponse = WebhookResponse(**response_json)
    assert webhook_response


def test_invalid_call_case(headers: Dict[str, str]) -> None:
    """Test invalid call_case."""
    response = client.post(
        url="/invalid_call_case",
        headers=headers,
        json={},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Unknown call_case: invalid_call_case"}


def test_invalid_json_format(headers: Dict[str, str]) -> None:
    """Test request with invalid JSON format."""
    response = client.post(
        url="/slot_filling",
        headers=headers,
        data="not a json",  # type:ignore # NOTE: test it will fail - we on purpose pass a string instead of a dict
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid JSON format"}


def test_invalid_request_format(valid_request_data: Dict[str, Any], headers: Dict[str, str]) -> None:
    """Test request with invalid format."""
    # Modify valid_request_data to be invalid here if needed
    invalid_request_data = valid_request_data
    invalid_request_data["queryResult"]["intent"] = {}

    response = client.post(
        url="/slot_filling",
        headers=headers,
        json=invalid_request_data
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid request format"}


def test_custom_code_execution(valid_request_data: Dict[str, Any], headers: Dict[str, str]) -> None:
    """Test request where custom code is executed."""
    # Add code to simulate custom code execution if necessary
    response = client.post(
        url="/response_refinement",
        headers=headers,
        json=valid_request_data
    )
    assert response.status_code == 200
    response_json: Dict[str, Any] = response.json()
    assert "fulfillmentMessages" in response_json
    assert "source" in response_json
    assert "payload" in response_json
    assert "outputContexts" in response_json

    webhook_response: WebhookResponse = WebhookResponse(**response_json)
    assert webhook_response

# Ensure you include other edge cases and scenarios as needed.
