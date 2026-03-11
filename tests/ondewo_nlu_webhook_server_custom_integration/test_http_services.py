import httpx
import pytest
import respx
from fastapi import HTTPException

from ondewo_nlu_webhook_server_custom_integration.http_services import make_http_request


class TestMakeHttpRequest:
    @respx.mock
    @pytest.mark.asyncio
    async def test_get_success(self) -> None:
        respx.get("https://example.com/api").mock(
            return_value=httpx.Response(200, json={"key": "value"})
        )
        result = await make_http_request("get", "https://example.com/api", headers={})
        assert result == {"key": "value"}

    @respx.mock
    @pytest.mark.asyncio
    async def test_post_with_json_payload(self) -> None:
        respx.post("https://example.com/api").mock(
            return_value=httpx.Response(201, json={"created": True})
        )
        result = await make_http_request(
            "post",
            "https://example.com/api",
            headers={},
            params={"q": "test"},
            json_payload={"data": "value"},
        )
        assert result == {"created": True}

    @respx.mock
    @pytest.mark.asyncio
    async def test_post_without_payload(self) -> None:
        respx.post("https://example.com/api").mock(
            return_value=httpx.Response(200, json={"ok": True})
        )
        result = await make_http_request(
            "post", "https://example.com/api", headers={}, params={"q": "1"}
        )
        assert result == {"ok": True}

    @respx.mock
    @pytest.mark.asyncio
    async def test_post_without_params(self) -> None:
        respx.post("https://example.com/api").mock(
            return_value=httpx.Response(200, json={"ok": True})
        )
        result = await make_http_request(
            "post",
            "https://example.com/api",
            headers={},
            json_payload={"data": "value"},
        )
        assert result == {"ok": True}

    @respx.mock
    @pytest.mark.asyncio
    async def test_delete_success(self) -> None:
        respx.delete("https://example.com/api/1").mock(
            return_value=httpx.Response(200, json={"deleted": True})
        )
        result = await make_http_request(
            "delete", "https://example.com/api/1", headers={}
        )
        assert result == {"deleted": True}

    @respx.mock
    @pytest.mark.asyncio
    async def test_put_success(self) -> None:
        respx.put("https://example.com/api/1").mock(
            return_value=httpx.Response(200, json={"updated": True})
        )
        result = await make_http_request(
            "put",
            "https://example.com/api/1",
            headers={},
            json_payload={"name": "new"},
        )
        assert result == {"updated": True}

    @pytest.mark.asyncio
    async def test_unsupported_method(self) -> None:
        with pytest.raises(HTTPException) as exc_info:
            await make_http_request("patch", "https://example.com/api", headers={})
        assert exc_info.value.status_code == 405

    @respx.mock
    @pytest.mark.asyncio
    async def test_server_error_status(self) -> None:
        respx.get("https://example.com/api").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )
        with pytest.raises(HTTPException) as exc_info:
            await make_http_request("get", "https://example.com/api", headers={})
        assert exc_info.value.status_code == 500

    @respx.mock
    @pytest.mark.asyncio
    async def test_invalid_json_response(self) -> None:
        respx.get("https://example.com/api").mock(
            return_value=httpx.Response(200, text="not json")
        )
        with pytest.raises(HTTPException) as exc_info:
            await make_http_request("get", "https://example.com/api", headers={})
        assert exc_info.value.status_code == 500
        assert "Invalid JSON" in exc_info.value.detail
