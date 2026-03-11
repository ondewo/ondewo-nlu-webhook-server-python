from unittest.mock import AsyncMock, patch

import pytest

from ondewo_nlu_webhook_server.server.base_models import (
    Context,
    EventInput,
    Intent,
    IntentMessage,
    IntentMessagePlatformEnum,
    IntentMessageText,
    Parameter,
    WebhookRequest,
    WebhookResponse,
)
from ondewo_nlu_webhook_server.server.relay import call_custom_code


def _make_request_and_response() -> tuple[WebhookRequest, WebhookResponse]:
    request = WebhookRequest.create_sample_request()
    response = WebhookResponse(
        fulfillmentText="",
        fulfillmentMessages=[
            IntentMessage(
                text=IntentMessageText(text=["hello"]),
                platform=IntentMessagePlatformEnum.PLATFORM_UNSPECIFIED.value,
            ),
        ],
        source="",
        payload={},
        outputContexts=request.queryResult.outputContexts,
        followupEventInput=EventInput(),
    )
    return request, response


class TestCallCustomCode:
    @pytest.mark.asyncio
    async def test_slot_filling(self) -> None:
        request, response = _make_request_and_response()
        with patch(
            "ondewo_nlu_webhook_server.server.relay.slot_filling",
            new_callable=AsyncMock,
            return_value=request.queryResult.outputContexts,
        ):
            result = await call_custom_code(request, response, "slot_filling")
            assert isinstance(result, WebhookResponse)

    @pytest.mark.asyncio
    async def test_response_refinement(self) -> None:
        request, response = _make_request_and_response()
        with patch(
            "ondewo_nlu_webhook_server.server.relay.response_refinement",
            new_callable=AsyncMock,
            return_value=([], request.queryResult.outputContexts),
        ):
            result = await call_custom_code(request, response, "response_refinement")
            assert isinstance(result, WebhookResponse)

    @pytest.mark.asyncio
    async def test_unknown_call_case_returns_response(self) -> None:
        request, response = _make_request_and_response()
        result = await call_custom_code(request, response, "unknown_case")
        assert result is response

    @pytest.mark.asyncio
    async def test_exception_returns_response(self) -> None:
        request, response = _make_request_and_response()
        with patch(
            "ondewo_nlu_webhook_server.server.relay.slot_filling",
            new_callable=AsyncMock,
            side_effect=RuntimeError("boom"),
        ):
            result = await call_custom_code(request, response, "slot_filling")
            assert result is response
