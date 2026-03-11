from unittest.mock import MagicMock, patch

import pytest

from ondewo_nlu_webhook_server.server.base_models import Context, Intent, Parameter
from ondewo_nlu_webhook_server_custom_integration.utils.helpers import (
    _append_message_to_fulfillment,
    add_text_to_fulfillment,
    check_if_text_response_exist,
    create_new_context_name,
    extract_price,
    get_index_of_text_entry,
    override_fulfillment_with_text,
    replace_placeholder_in_text,
)


class TestCheckIfTextResponseExist:
    def test_empty_list(self) -> None:
        assert check_if_text_response_exist([]) is False

    def test_message_with_text(self) -> None:
        msgs = [{"text": {"text": ["hello"]}}]
        assert check_if_text_response_exist(msgs) is True

    def test_message_without_text_key(self) -> None:
        msgs = [{"image": {"url": "http://example.com"}}]
        assert check_if_text_response_exist(msgs) is False

    def test_message_with_text_key_but_no_nested_text(self) -> None:
        msgs = [{"text": {"other": "value"}}]
        assert check_if_text_response_exist(msgs) is False


class TestGetIndexOfTextEntry:
    def test_finds_text_entry(self) -> None:
        msgs = [{"image": {}}, {"text": {"text": ["hi"]}}]
        assert get_index_of_text_entry(msgs) == 1

    def test_raises_when_no_text(self) -> None:
        with pytest.raises(ValueError, match="Could not find text entries"):
            get_index_of_text_entry([{"image": {}}])


class TestAppendMessageToFulfillment:
    def test_appends_new_message(self) -> None:
        msgs: list = []
        result = _append_message_to_fulfillment(msgs, "hello")
        assert len(result) == 1
        assert result[0]["text"]["text"] == ["hello"]


class TestAddTextToFulfillment:
    def test_adds_to_existing_text(self) -> None:
        msgs = [{"text": {"text": ["hello"]}}]
        result = add_text_to_fulfillment(msgs, "world")
        assert result[0]["text"]["text"] == ["hello", "world"]

    def test_creates_new_text_entry(self) -> None:
        msgs = [{"image": {}}]
        result = add_text_to_fulfillment(msgs, "hello")
        assert len(result) == 2
        assert result[1]["text"]["text"] == ["hello"]


class TestOverrideFulfillmentWithText:
    def test_override_existing(self) -> None:
        msgs = [{"text": {"text": ["old"]}}]
        result = override_fulfillment_with_text(msgs, "new")
        assert result[0]["text"]["text"] == ["new"]

    def test_override_no_existing(self) -> None:
        msgs = [{"image": {}}]
        result = override_fulfillment_with_text(msgs, "new")
        assert len(result) == 2
        assert result[1]["text"]["text"] == ["new"]


class TestCreateNewContextName:
    def test_with_active_contexts(self) -> None:
        contexts = [
            Context(
                name="projects/my-project/agent/sessions/my-session/active_contexts/ctx1",
                lifespanCount=5,
                parameters={},
            ),
        ]
        result = create_new_context_name(contexts, "new_ctx")
        assert "projects/my-project/agent/sessions/my-session/active_contexts/new_ctx" == result

    def test_with_project_and_session_id(self) -> None:
        result = create_new_context_name([], "new_ctx", project_id="proj1", session_id="sess1")
        assert result == "projects/proj1/agent/sessions/sess1/active_contexts/new_ctx"

    def test_raises_without_contexts_or_ids(self) -> None:
        with pytest.raises(ValueError, match="at least one active context"):
            create_new_context_name([], "new_ctx")


class TestReplacePlaceholderInText:
    def test_welcome_intent_replacement(self) -> None:
        msgs = [{"text": {"text": ["Hello <organization_name>!"]}}]
        intent = Intent(name="id", displayName="Default Welcome Intent")
        result = replace_placeholder_in_text(msgs, "ACME Corp", intent, None)
        assert result[0]["text"]["text"][0] == "Hello ACME Corp!"

    def test_no_placeholder(self) -> None:
        msgs = [{"text": {"text": ["Hello world"]}}]
        intent = Intent(name="id", displayName="Default Welcome Intent")
        result = replace_placeholder_in_text(msgs, "ACME", intent, None)
        assert result[0]["text"]["text"][0] == "Hello world"

    def test_unknown_intent_no_replacement(self) -> None:
        msgs = [{"text": {"text": ["Hello <name>"]}}]
        intent = Intent(name="id", displayName="some_other_intent")
        result = replace_placeholder_in_text(msgs, "value", intent, None)
        assert result[0]["text"]["text"][0] == "Hello <name>"

    def test_message_without_text(self) -> None:
        msgs = [{"image": {"url": "http://example.com"}}]
        intent = Intent(name="id", displayName="Default Welcome Intent")
        result = replace_placeholder_in_text(msgs, "value", intent, None)
        assert result == msgs


class TestExtractPrice:
    def test_extract_price_parses_table(self) -> None:
        html = """
        <html><body>
        <div class="table-box">
            <table class="table">
                <tr class="tablerow">
                    <td>Category A</td>
                    <td>10.99€</td>
                </tr>
                <tr class="tablerow">
                    <td>Category B</td>
                    <td>20.50€</td>
                </tr>
            </table>
        </div>
        </body></html>
        """
        mock_response = MagicMock()
        mock_response.text = html
        mock_response.raise_for_status = MagicMock()

        with patch(
            "ondewo_nlu_webhook_server_custom_integration.utils.helpers.get",
            return_value=mock_response,
        ):
            result = extract_price("https://example.com")
            assert "price_list" in result
            assert len(result["price_list"]) == 2
            assert result["price_list"][0]["category"] == "Category A"
            assert result["price_list"][0]["price"] == "10.99€"
