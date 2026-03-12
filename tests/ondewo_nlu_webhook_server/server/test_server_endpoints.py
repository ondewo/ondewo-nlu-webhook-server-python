from typing import Any

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPBasicCredentials
from fastapi.testclient import TestClient

from ondewo_nlu_webhook_server.globals import WebhookGlobals
from ondewo_nlu_webhook_server.server.__main__ import app
from ondewo_nlu_webhook_server.server.server import (
    verify_credentials,
    verify_token,
)
from ondewo_nlu_webhook_server.version import __version__


client = TestClient(app)


class TestHealthAndIndex:
    def test_health_check(self) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_health_check_response_body_structure(self) -> None:
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"

    def test_index(self) -> None:
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert __version__ in data["message"]

    def test_index_message_contains_ondewo(self) -> None:
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "ONDEWO" in data["message"]

    def test_invalid_credentials(self, valid_request_data: dict[str, Any]) -> None:
        response = client.post(
            url="/slot_filling",
            headers={"Authorization": "Basic d3Jvbmc6Y3JlZHM="},  # wrong:creds
            json=valid_request_data,
        )
        assert response.status_code == 401


class TestVerifyToken:
    def test_verify_token_invalid(self) -> None:
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token="invalid_token")
        assert exc_info.value.status_code == 401

    def test_verify_token_valid(self) -> None:
        valid_token: str = WebhookGlobals.ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_BEARER
        result: str = verify_token(token=valid_token)
        assert result == valid_token

    def test_verify_credentials_invalid(self) -> None:
        creds = HTTPBasicCredentials(username="wrong", password="wrong")
        with pytest.raises(HTTPException) as exc_info:
            verify_credentials(credentials=creds)
        assert exc_info.value.status_code == 401

    def test_verify_credentials_valid(self) -> None:
        valid_username: str = WebhookGlobals.ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_HTTP_BASIC_AUTH_USERNAME
        valid_password: str = WebhookGlobals.ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_HTTP_BASIC_AUTH_PASSWORD
        creds = HTTPBasicCredentials(username=valid_username, password=valid_password)
        result: HTTPBasicCredentials = verify_credentials(credentials=creds)
        assert result == creds
