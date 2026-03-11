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
)

from bs4 import BeautifulSoup
from loguru import logger
from requests import get

from ondewo_nlu_webhook_server.server.base_models import (
    Context,
    Intent,
)


def add_text_to_fulfillment(fulfillment_messages: list[dict[str, Any]], text: str) -> list[dict[str, Any]]:
    """Add an entry to the text section of the fulfillment messages.

    Args:
        fulfillment_messages: list of fulfillment messages
        text: text to add to the text section of the fulfillment messages

    Returns:
        list of fulfillment messages with new text added
    """
    if check_if_text_response_exist(fulfillment_messages):
        idx: int = get_index_of_text_entry(fulfillment_messages)
        fulfillment_messages[idx]["text"]["text"].append(text)
        return fulfillment_messages
    return _append_message_to_fulfillment(fulfillment_messages, text)


def check_if_text_response_exist(fulfillment_messages: list[dict[str, Any]]) -> bool:
    """Check if a text response exists in the provided fulfillment messages.

    Args:
        fulfillment_messages: A list of fulfillment messages.

    Returns:
        True if any message contains a "text" field with content, otherwise False.
    """
    if len(fulfillment_messages) >= 1 and any("text" in message for message in fulfillment_messages):
        message_with_text: dict[str, Any] | None = None
        for message in fulfillment_messages:
            if "text" in message:
                message_with_text = message
                break
        if message_with_text and "text" in message_with_text["text"]:
            return True
    return False


def override_fulfillment_with_text(
    fulfillment_messages: list[dict[str, Any]],
    text: str,
) -> list[dict[str, Any]]:
    """Override the current text in the fulfillment messages with the given text string.

    Args:
        fulfillment_messages: A list of fulfillment messages.
        text: The new text to set in the fulfillment message's "text" field.

    Returns:
        The updated list of fulfillment messages.
    """
    if check_if_text_response_exist(fulfillment_messages):
        idx: int = get_index_of_text_entry(fulfillment_messages)
        fulfillment_messages[idx]["text"]["text"] = [text]
        return fulfillment_messages
    return _append_message_to_fulfillment(fulfillment_messages, text)


def _append_message_to_fulfillment(
    fulfillment_messages: list[dict[str, Any]],
    text: str,
) -> list[dict[str, Any]]:
    """Append a new text message to the list of fulfillment messages.

    Args:
        fulfillment_messages: A list of fulfillment messages.
        text: The new text to append as a message.

    Returns:
        The updated list of fulfillment messages with the new text message appended.
    """
    fulfillment_messages.append({"text": {"text": [text]}})
    return fulfillment_messages


def get_index_of_text_entry(fulfillment_messages: list[dict[str, Any]]) -> int:
    """Search for the index of the first message containing a "text" field.

    Args:
        fulfillment_messages: A list of dictionaries representing the fulfillment messages.

    Returns:
        The index of the first message containing the "text" field.

    Raises:
        ValueError: If no message containing a "text" field is found in the list.
    """
    for idx, entry in enumerate(fulfillment_messages):
        if "text" in entry:
            return idx
    raise ValueError(f"Could not find text entries! messages: {fulfillment_messages!s}")


def create_new_context_name(
    active_contexts: list[Context],
    context_name: str,
    project_id: str | None = None,
    session_id: str | None = None,
) -> str:
    """Create a compatible context name from the given string.

    Args:
        active_contexts: A list of active contexts.
        context_name: The name of the new context.
        project_id: The project ID to use if there are no active contexts.
        session_id: The session ID to use if there are no active contexts.

    Returns:
        A string representing the compatible context name.

    Raises:
        ValueError: If neither active contexts nor both project_id and session_id are provided.
    """
    if not project_id and not session_id:
        if len(active_contexts) < 1:
            raise ValueError(
                "If no project ID and session ID are provided, at least one active context is needed "
                + "to extract project and session IDs",
            )
        some_context_name: str = active_contexts[0].name
        project_id = some_context_name.split("projects/")[1].split("/agent")[0]
        session_id = some_context_name.split("sessions/")[1].split("/active_contexts")[0]

    return f"projects/{project_id}/agent/sessions/{session_id}/active_contexts/{context_name}"


def replace_placeholder_in_text(
    fulfillment_messages: list[dict[str, Any]],
    replace_text: str,
    active_intent: Intent,
    parameters: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Replace the placeholder '<>' in the 'text' field of fulfillment messages.

    Args:
        fulfillment_messages: A list of fulfillment messages.
        replace_text: The value to replace the placeholder in the text message.
        active_intent: The current intent associated with the request.
        parameters: Additional context or parameters.

    Returns:
        The updated list of fulfillment messages with the placeholder replaced.
    """
    for message in fulfillment_messages:
        if "text" in message and "text" in message["text"]:
            for i, message_text in enumerate(message["text"]["text"]):
                if "<" in message_text and ">" in message_text:
                    if active_intent.displayName == "Default Welcome Intent":
                        message["text"]["text"][i] = message_text.replace("<organization_name>", replace_text)

                    elif active_intent.displayName in ["i.example_webrequest"]:
                        url: str = "https://www.myurl.com/my-page"
                        data: dict[str, list[dict[str, str]]] = extract_price(url)
                        assert parameters
                        parameter_type: str = parameters["MyEntityType"][0]
                        price: str
                        if parameter_type == "parameter1":
                            price_match: str | None = next(
                                (
                                    item["price"]
                                    for item in data["my-product-1"]
                                    if "my-product-category" in item["category"]
                                ),
                                None,
                            )
                            assert price_match is not None
                            price = price_match[:-2]
                        else:
                            price_match_2: str | None = next(
                                (
                                    item["price"]
                                    for item in data["my-product-2"]
                                    if "my-product-category" in item["category"]
                                ),
                                None,
                            )
                            assert price_match_2 is not None
                            price = price_match_2[:-2]

                        assert price is not None
                        message["text"]["text"][i] = message_text.replace(replace_text, price)

                    else:
                        logger.debug("Nothing to replace.")

    return fulfillment_messages


def extract_price(url: str) -> dict[str, list[dict[str, str]]]:
    """Extract price information from a webpage containing a structured HTML table.

    Args:
        url: The URL of the webpage containing the price table.

    Returns:
        A dictionary containing a list of extracted price entries.

    Raises:
        requests.exceptions.RequestException: If there is an issue with the HTTP request.
        AssertionError: If the expected table or rows are not found in the HTML.
    """
    response = get(url, timeout=30)
    response.raise_for_status()

    soup: BeautifulSoup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("div", class_="table-box").find("table", class_="table")  # type: ignore
    assert table is not None
    rows = table.find_all("tr", class_="tablerow")  # type: ignore
    assert rows is not None

    values: list[dict[str, str]] = []
    for row in rows:
        cells = row.find_all("td")
        if len(cells) >= 2:
            category: str = cells[0].get_text(strip=True)
            price: str = cells[1].get_text(strip=True)
            values.append(
                {
                    "category": category,
                    "price": price,
                },
            )

    return {"price_list": values}
