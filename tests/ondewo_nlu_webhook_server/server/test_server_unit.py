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

import json
from typing import (
    Any,
)

import pytest
from fastapi.testclient import TestClient

from ondewo_nlu_webhook_server.globals import WebhookGlobals
from ondewo_nlu_webhook_server.server.__main__ import app
from ondewo_nlu_webhook_server.server.base_models import WebhookResponse
from ondewo_nlu_webhook_server.server.server import verify_token


client = TestClient(app)


def test_valid_request(valid_request_data: dict[str, Any], headers: dict[str, str]) -> None:
    """Test valid request with known call_case."""
    response = client.post(
        url="/slot_filling",
        headers=headers,
        json=valid_request_data,
    )
    assert response.status_code == 200
    response_json: dict[str, Any] = response.json()
    assert "fulfillmentMessages" in response_json
    assert "source" in response_json
    assert "payload" in response_json
    assert "outputContexts" in response_json

    webhook_response: WebhookResponse = WebhookResponse(**response_json)
    assert webhook_response


def test_invalid_call_case(headers: dict[str, str]) -> None:
    """Test invalid call_case."""
    response = client.post(
        url="/invalid_call_case",
        headers=headers,
        json={},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Unknown call_case: invalid_call_case"}


def test_invalid_json_format(headers: dict[str, str]) -> None:
    """Test request with invalid JSON format."""
    response = client.post(
        url="/slot_filling",
        headers=headers,
        data="not a json",  # type: ignore[arg-type] # NOTE: test it will fail - we on purpose pass a string instead of a dict
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid JSON format"}


def test_invalid_request_format(valid_request_data: dict[str, Any], headers: dict[str, str]) -> None:
    """Test request with invalid format."""
    # Modify valid_request_data to be invalid here if needed
    invalid_request_data = valid_request_data
    invalid_request_data["queryResult"]["intent"] = {}

    response = client.post(
        url="/slot_filling",
        headers=headers,
        json=invalid_request_data,
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid request format"}


def test_custom_code_execution(valid_request_data: dict[str, Any], headers: dict[str, str]) -> None:
    """Test request where custom code is executed."""
    # Add code to simulate custom code execution if necessary
    response = client.post(
        url="/response_refinement",
        headers=headers,
        json=valid_request_data,
    )
    assert response.status_code == 200
    response_json: dict[str, Any] = response.json()
    assert "fulfillmentMessages" in response_json
    assert "source" in response_json
    assert "payload" in response_json
    assert "outputContexts" in response_json

    webhook_response: WebhookResponse = WebhookResponse(**response_json)
    assert webhook_response


# Ensure you include other edge cases and scenarios as needed.


@pytest.mark.unit
def test_verify_token_valid() -> None:
    """Test verify_token returns the token when it matches the configured bearer token."""
    valid_token: str = WebhookGlobals.ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_BEARER
    result: str = verify_token(token=valid_token)
    assert result == valid_token


@pytest.mark.unit
def test_string_json_body(valid_request_data: dict[str, Any], headers: dict[str, str]) -> None:
    """Test request where the JSON body is a double-encoded string (isinstance(request_json, str) branch)."""
    double_encoded: str = json.dumps(json.dumps(valid_request_data))
    merged_headers: dict[str, str] = {**headers, "Content-Type": "application/json"}
    response = client.post(
        url="/slot_filling",
        headers=merged_headers,
        content=double_encoded,
    )
    assert response.status_code == 200
    response_json: dict[str, Any] = response.json()
    assert "fulfillmentMessages" in response_json


@pytest.mark.unit
def test_invalid_string_json_body(headers: dict[str, str]) -> None:
    """Test request where the JSON body is a double-encoded string that decodes to an invalid WebhookRequest."""
    invalid_inner: dict[str, Any] = {"queryResult": {"intent": {}}}
    double_encoded: str = json.dumps(json.dumps(invalid_inner))
    merged_headers: dict[str, str] = {**headers, "Content-Type": "application/json"}
    response = client.post(
        url="/slot_filling",
        headers=merged_headers,
        content=double_encoded,
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid request format"}
