from typing import Any

from fastapi.testclient import TestClient

from ondewo_nlu_webhook_server.server.__main__ import app
from ondewo_nlu_webhook_server.version import __version__

client = TestClient(app)


class TestHealthAndIndex:
    def test_health_check(self) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_index(self) -> None:
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert __version__ in data["message"]

    def test_invalid_credentials(self, valid_request_data: dict[str, Any]) -> None:
        response = client.post(
            url="/slot_filling",
            headers={"Authorization": "Basic d3Jvbmc6Y3JlZHM="},  # wrong:creds
            json=valid_request_data,
        )
        assert response.status_code == 401


class TestVerifyToken:
    def test_verify_token_invalid(self) -> None:
        from ondewo_nlu_webhook_server.server.server import verify_token
        from fastapi import HTTPException
        import pytest

        with pytest.raises(HTTPException) as exc_info:
            verify_token(token="invalid_token")
        assert exc_info.value.status_code == 401

    def test_verify_credentials_invalid(self) -> None:
        from ondewo_nlu_webhook_server.server.server import verify_credentials
        from fastapi import HTTPException
        from fastapi.security import HTTPBasicCredentials
        import pytest

        creds = HTTPBasicCredentials(username="wrong", password="wrong")
        with pytest.raises(HTTPException) as exc_info:
            verify_credentials(credentials=creds)
        assert exc_info.value.status_code == 401
