import importlib
import sys
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def _mock_nlu_client(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock the NluClient before auth module is imported to prevent gRPC connection."""
    # If already imported, remove it so we can reimport with mocks
    for mod_name in list(sys.modules.keys()):
        if "ondewo_nlu_webhook_server_custom_integration.auth" in mod_name:
            del sys.modules[mod_name]


def _get_auth_module(mock_client: MagicMock) -> object:
    """Import auth module with mocked NluClient."""
    mock_client_class = MagicMock(return_value=mock_client)
    with patch.dict(
        "os.environ",
        {
            "ONDEWO_NLU_CAI_HOST": "localhost",
            "ONDEWO_NLU_CAI_PORT": "50055",
            "ONDEWO_NLU_CAI_HTTP_BASIC_AUTH_TOKEN": "token",
            "ONDEWO_NLU_CAI_USER_NAME": "user",
            "ONDEWO_NLU_CAI_USER_PASS": "pass",
            "ONDEWO_NLU_CAI_GRPC_CERT": "",
        },
    ), patch("ondewo.nlu.client.Client", mock_client_class):
        if "ondewo_nlu_webhook_server_custom_integration.auth" in sys.modules:
            del sys.modules["ondewo_nlu_webhook_server_custom_integration.auth"]
        import ondewo_nlu_webhook_server_custom_integration.auth as auth_module

        auth_module.nlu_client = mock_client
        return auth_module


class TestLogin:
    def test_login_success(self) -> None:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.authToken = "test-token"
        mock_client.services.users.login.return_value = mock_response

        auth = _get_auth_module(mock_client)
        result = auth.login()  # type: ignore
        assert result is not None
        assert result.authToken == "test-token"

    def test_login_failure(self) -> None:
        mock_client = MagicMock()
        mock_client.services.users.login.side_effect = Exception("connection refused")

        auth = _get_auth_module(mock_client)
        with pytest.raises(Exception, match="connection refused"):
            auth.login()  # type: ignore

    def test_login_missing_auth_token(self) -> None:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.authToken = ""
        mock_client.services.users.login.return_value = mock_response

        auth = _get_auth_module(mock_client)
        with pytest.raises(ValueError, match="auth token is missing"):
            auth.login()  # type: ignore


class TestGetIntent:
    def test_get_intent_success(self) -> None:
        mock_client = MagicMock()
        mock_intent = MagicMock()
        mock_client.services.intents.get_intent.return_value = mock_intent

        auth = _get_auth_module(mock_client)
        result = auth.get_intent()  # type: ignore
        assert result is mock_intent

    def test_get_intent_failure(self) -> None:
        mock_client = MagicMock()
        mock_client.services.intents.get_intent.side_effect = Exception("not found")

        auth = _get_auth_module(mock_client)
        result = auth.get_intent()  # type: ignore
        assert result is None
