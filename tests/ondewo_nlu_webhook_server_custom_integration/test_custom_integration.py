from unittest.mock import patch

import pytest

from ondewo_nlu_webhook_server.server.base_models import Context, Intent
from ondewo_nlu_webhook_server_custom_integration.custom_integration import (
    IntentMapping,
    response_refinement,
    slot_filling,
)


class TestIntentMapping:
    def test_values(self) -> None:
        assert IntentMapping.DEFAULT_WELCOME_INTENT.value == "Default Welcome Intent"
        assert IntentMapping.DEFAULT_FALLBACK_INTENT.value == "Default Fallback Intent"
        assert IntentMapping.I_EXAMPLE_WEBREQUEST.value == "i.example_webrequest"


class TestSlotFilling:
    @pytest.mark.asyncio
    async def test_known_intent(self) -> None:
        intent = Intent(name="id", displayName="Default Welcome Intent")
        contexts = [Context(name="ctx", lifespanCount=1, parameters={})]
        result = await slot_filling(active_intent=intent, active_contexts=contexts)
        assert result == contexts

    @pytest.mark.asyncio
    async def test_unknown_intent(self) -> None:
        intent = Intent(name="id", displayName="unknown_intent")
        result = await slot_filling(active_intent=intent)
        assert result is None

    @pytest.mark.asyncio
    async def test_thanks_good_intent(self) -> None:
        intent = Intent(name="id", displayName="i.example_thanks_good")
        result = await slot_filling(active_intent=intent, active_contexts=[])
        assert result == []

    @pytest.mark.asyncio
    async def test_my_date_intent(self) -> None:
        intent = Intent(name="id", displayName="i.example_my-date")
        result = await slot_filling(active_intent=intent, active_contexts=[])
        assert result == []


class TestResponseRefinement:
    @pytest.mark.asyncio
    async def test_welcome_intent(self) -> None:
        intent = Intent(name="id", displayName="Default Welcome Intent")
        msgs = [{"text": {"text": ["Hello"]}}]
        result_msgs, result_ctx = await response_refinement(
            headers={},
            active_intent=intent,
            fulfillment_messages=msgs,
            active_contexts=None,
            parameters=None,
        )
        assert result_msgs == msgs

    @pytest.mark.asyncio
    async def test_fallback_intent(self) -> None:
        intent = Intent(name="id", displayName="Default Fallback Intent")
        msgs = [{"text": {"text": ["Sorry"]}}]
        result_msgs, result_ctx = await response_refinement(
            headers={},
            active_intent=intent,
            fulfillment_messages=msgs,
            active_contexts=None,
            parameters=None,
        )
        assert result_msgs == msgs

    @pytest.mark.asyncio
    async def test_unknown_intent(self) -> None:
        intent = Intent(name="id", displayName="some_other_intent")
        msgs = [{"text": {"text": ["Hi"]}}]
        result_msgs, result_ctx = await response_refinement(
            headers={},
            active_intent=intent,
            fulfillment_messages=msgs,
            active_contexts=None,
            parameters=None,
        )
        assert result_msgs == msgs

    @pytest.mark.asyncio
    async def test_thanks_good_intent(self) -> None:
        intent = Intent(name="id", displayName="i.example_thanks_good")
        msgs = [{"text": {"text": ["Thanks"]}}]
        result_msgs, result_ctx = await response_refinement(
            headers={},
            active_intent=intent,
            fulfillment_messages=msgs,
            active_contexts=[],
            parameters=None,
        )
        assert result_msgs == msgs

    @pytest.mark.asyncio
    async def test_webrequest_intent_calls_replace_placeholder(self) -> None:
        intent = Intent(name="id", displayName=IntentMapping.I_EXAMPLE_WEBREQUEST.value)
        msgs = [{"text": {"text": ["Value: <EXAMPLE_PLACEHOLDER>"]}}]
        params = {"key": "value"}
        refined_msgs = [{"text": {"text": ["Value: replaced"]}}]

        with patch(
            "ondewo_nlu_webhook_server_custom_integration.custom_integration.replace_placeholder_in_text",
            return_value=refined_msgs,
        ) as mock_replace:
            result_msgs, result_ctx = await response_refinement(
                headers={},
                active_intent=intent,
                fulfillment_messages=msgs,
                active_contexts=None,
                parameters=params,
            )

        mock_replace.assert_called_once_with(
            fulfillment_messages=msgs,
            replace_text="<EXAMPLE_PLACEHOLDER>",
            active_intent=intent,
            parameters=params,
        )
        assert result_msgs == refined_msgs
        assert result_ctx is None

    @pytest.mark.asyncio
    async def test_default_exit_intent_goes_to_else_branch(self) -> None:
        intent = Intent(name="id", displayName=IntentMapping.DEFAULT_EXIT_INTENT.value)
        msgs = [{"text": {"text": ["Goodbye"]}}]

        with patch(
            "ondewo_nlu_webhook_server_custom_integration.custom_integration.replace_placeholder_in_text",
        ) as mock_replace:
            result_msgs, result_ctx = await response_refinement(
                headers={},
                active_intent=intent,
                fulfillment_messages=msgs,
                active_contexts=None,
                parameters=None,
            )

        mock_replace.assert_not_called()
        assert result_msgs == msgs

    @pytest.mark.asyncio
    async def test_default_reset_intent_goes_to_else_branch(self) -> None:
        intent = Intent(name="id", displayName=IntentMapping.DEFAULT_RESET_INTENT.value)
        msgs = [{"text": {"text": ["Reset"]}}]

        with patch(
            "ondewo_nlu_webhook_server_custom_integration.custom_integration.replace_placeholder_in_text",
        ) as mock_replace:
            result_msgs, result_ctx = await response_refinement(
                headers={},
                active_intent=intent,
                fulfillment_messages=msgs,
                active_contexts=None,
                parameters=None,
            )

        mock_replace.assert_not_called()
        assert result_msgs == msgs
