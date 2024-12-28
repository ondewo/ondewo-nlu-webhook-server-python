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
    List,
    Optional,
)

from bs4 import BeautifulSoup
from ondewo.logging.logger import logger_console as log
from requests import get

from ondewo_nlu_webhook_server.server.base_models import (
    Context,
    Intent,
)


def add_text_to_fulfillment(fulfillment_messages: List[Dict[str, Any]], text: str) -> List[Dict[str, Any]]:
    """
    add an entry to the text section of the fulfillment messages
    if no text entries are in the messages, a text entry with the desired text will be created

    Args:
        fulfillment_messages (List[Dict[str, Any]]): list of fulfillment messages
        text (str): text to add to the text section of the fulfillment messages

    Returns:
        list of fulfillment messages with new text added
    """
    if check_if_text_response_exist(fulfillment_messages):
        idx = get_index_of_text_entry(fulfillment_messages)
        fulfillment_messages[idx]["text"]["text"].append(text)
        return fulfillment_messages
    else:
        return _append_message_to_fulfillment(fulfillment_messages, text)


def check_if_text_response_exist(fulfillment_messages: List[Dict[str, Any]]) -> bool:
    """
    Checks if a text response exists in the provided fulfillment messages.

    This function examines a list of fulfillment messages (commonly from a chatbot or
    messaging platform) and determines whether any of the messages contain a "text"
    field with content.

    Args:
        fulfillment_messages (List[Dict[str, Any]]): A list of fulfillment messages,
        where each message is a dictionary that may contain a "text" key.

    Returns:
        bool: True if any message contains a "text" field with content,
        otherwise False.
    """
    if len(fulfillment_messages) >= 1:
        if any("text" in message.keys() for message in fulfillment_messages):
            for message in fulfillment_messages:
                if "text" in message.keys():
                    break
            if "text" in message["text"].keys():  # type: ignore
                return True
    return False


def override_fulfillment_with_text(
    fulfillment_messages: List[Dict[str, Any]], text: str,
) -> List[Dict[str, Any]]:
    """
    Overrides the current text in the fulfillment messages with the given text string.

    This function checks if the fulfillment messages already contain a "text" entry. If so,
    it updates the content of the first "text" field with the provided `text` value.
    If no "text" entry is found, it appends a new message with the given text.

    Args:
        fulfillment_messages (List[Dict[str, Any]]): A list of fulfillment messages, where
            each message may contain various fields, including a "text" field.
        text (str): The new text to set in the fulfillment message's "text" field.

    Returns:
        List[Dict[str, Any]]: The updated list of fulfillment messages, with the "text" field
        overridden or appended based on the current state of the messages.
    """
    if check_if_text_response_exist(fulfillment_messages):
        idx = get_index_of_text_entry(fulfillment_messages)
        fulfillment_messages[idx]["text"]["text"] = [text]
        return fulfillment_messages
    else:
        return _append_message_to_fulfillment(fulfillment_messages, text)


def _append_message_to_fulfillment(
    fulfillment_messages: List[Dict[str, Any]],
    text: str,
) -> List[Dict[str, Any]]:
    """
    Appends a new text message to the list of fulfillment messages.

    This function adds a new message with the provided text to the `fulfillment_messages` list.
    It does not check for existing "text" messages and does not override any existing messages.
    A new message will always be appended.

    **Important**: This function should not be used directly without ensuring that the
    `check_if_text_response_exist()` function has been called beforehand to confirm that
    appending a new message is the desired behavior.

    Args:
        fulfillment_messages (List[Dict[str, Any]]): A list of fulfillment messages,
            where each message may contain different fields such as "text", "payload", etc.
        text (str): The new text to append as a message to the `fulfillment_messages` list.

    Returns:
        List[Dict[str, Any]]: The updated list of fulfillment messages with the new text message appended.

    Notes:
        - **DO NOT** use this function directly without verifying the existence of a "text" response
          using `check_if_text_response_exist()`. This function does not prevent appending multiple
          "text" messages.
        - This function will **not** modify or override any existing "text" entries in the messages.
        - It is primarily for use cases where appending a new text message is necessary without
          considering existing "text" messages.
    """
    fulfillment_messages.append({"text": {"text": [text]}})
    return fulfillment_messages


def get_index_of_text_entry(fulfillment_messages: List[Dict[str, Any]]) -> int:
    """
    Searches for the index of the first message containing a "text" field in the
    given list of fulfillment messages.

    This function iterates through the `fulfillment_messages` list and returns the index
    of the first entry that contains a "text" field. If no such message is found,
    it raises a `ValueError`.

    Args:
        fulfillment_messages (List[Dict[str, Any]]): A list of dictionaries representing
            the fulfillment messages. Each message may contain various fields, and this
            function looks for the "text" field specifically.

    Returns:
        int: The index of the first message containing the "text" field.

    Raises:
        ValueError: If no message containing a "text" field is found in the list.
    """
    for idx, entry in enumerate(fulfillment_messages):
        if "text" in entry.keys():
            return idx
    raise ValueError(f"Could not find text entries! messages: {str(fulfillment_messages)}")


def create_new_context_name(
    active_contexts: List[Context],
    context_name: str,
    project_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> str:
    """
    Creates a compatible context name from the given string by either extracting the correct project
    and session IDs from an active context, or by constructing it from the provided input.

    Args:
        active_contexts (List[Context]): A list of active contexts. If provided, the function will
            extract the project and session IDs from the first context in the list.
        context_name (str): The name of the new context (e.g., "my-context-999").
        project_id (Optional[str]): The project ID to use if there are no active contexts.
            If not provided and no active contexts exist, this must be supplied.
        session_id (Optional[str]): The session ID to use if there are no active contexts.
            If not provided and no active contexts exist, this must be supplied.

    Returns:
        str: A string representing the compatible context name in the format:
            "projects/<PROJECT-ID>/agent/sessions/<SESSION-ID>/contexts/<context_name>"

    Raises:
        ValueError: If neither active contexts nor both project_id and session_id are provided.
    """
    if not project_id and not session_id:
        if len(active_contexts) < 1:
            raise ValueError(
                "If no project ID and session ID are provided, at least one active context is needed "
                + "to extract project and session IDs",
            )
        some_context_name = active_contexts[0].name
        project_id = some_context_name.split("projects/")[1].split("/agent")[0]
        session_id = some_context_name.split("sessions/")[1].split("/active_contexts")[0]

    return f"projects/{project_id}/agent/sessions/{session_id}/active_contexts/{context_name}"


def replace_placeholder_in_text(
    fulfillment_messages: List[Dict[str, Any]],
    replace_text: str,
    active_intent: Intent,
    parameters: Optional[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Replaces the placeholder '<>' in the 'text' field of fulfillment messages with the provided ID value.

    This function searches for a placeholder (`<>`) in the text field of the fulfillment messages
    and replaces it with the provided `replace_text`. If the placeholder is not found, the list
    of fulfillment messages is returned without modification. The function supports optional
    parameters, including `active_intent` and additional context in `parameters`.

    Args:
        fulfillment_messages (List[Dict[str, Any]]): A list of fulfillment messages.
            Each message can contain various fields, including "text".
        replace_text (str): The value to replace the placeholder (`<>`) in the text message.
        active_intent (Intent): The current intent associated with the request, which may
            influence how the placeholder is replaced.
        parameters (Optional[Dict[str, Any]], optional): Additional context or parameters
            that may be used during the placeholder replacement (default is None).

    Returns:
        List[Dict[str, Any]]: The updated list of fulfillment messages with the placeholder replaced.

    """
    for message in fulfillment_messages:
        if "text" in message and "text" in message["text"]:
            for i, message_text in enumerate(message["text"]["text"]):
                if "<" in message_text and ">" in message_text:

                    # Default Welcome Intent
                    if active_intent.displayName == "Default Welcome Intent":
                        message["text"]["text"][i] = message_text.replace("<organization_name>", replace_text)

                    elif active_intent.displayName in ["i.example_webrequest"]:  # TODO: Example Intent, use yours
                        url: str = "https://www.myurl.com/my-page"
                        data = extract_price(url)
                        assert parameters
                        parameter_type: str = parameters['MyEntityType'][0]  # TODO: example entity type, use yours
                        price: str
                        if parameter_type == "parameter1":  # TODO: example parameter, use yours
                            price = next(
                                (
                                    item["price"] for item in data['my-product-1'] if  # type: ignore
                                    "my-product-category" in item["category"]
                                ), None,
                            )[:-2]
                        else:
                            price = next(
                                (
                                    item["price"] for item in data['my-product-2'] if  # type: ignore
                                    "my-product-category" in item["category"]
                                ), None,
                            )[:-2]

                        assert price is not None
                        # replace with correct price based on TypeOfVehicle
                        message["text"]["text"][i] = message_text.replace(replace_text, price)

                    else:
                        log.debug("Nothing to replace.")

    return fulfillment_messages


def extract_price(url: str) -> Dict[str, List[Dict[str, str]]]:
    """
    Extracts price information from a webpage containing a structured HTML table.

    This function fetches the webpage from the provided URL, parses it using BeautifulSoup,
    and extracts price-related data from a specific table. The extracted data includes
    categories, prices, and optional notes.

    Args:
        url (str): The URL of the webpage containing the price table.

    Returns:
        Dict[str, List[Dict[str, str]]]: A dictionary containing a list of extracted price entries.
        Each entry is a dictionary with the following keys:
            - "category" (str): The category name from the first column.
            - "price" (str): The price from the second column.

    Raises:
        requests.exceptions.RequestException: If there is an issue with the HTTP request.
        AssertionError: If the expected table or rows are not found in the HTML.
    """
    response = get(url)
    response.raise_for_status()  # Ensure the request was successful

    soup: BeautifulSoup = BeautifulSoup(response.text, "html.parser")

    # Find the table containing the data
    table = soup.find("div", class_="table-box").find("table", class_="table")  # type: ignore
    assert table is not None
    rows = table.find_all("tr", class_="tablerow")  # type:ignore
    assert rows is not None

    values: List = []
    # Parse the rows for data
    for row in rows:
        cells = row.find_all("td")
        if len(cells) >= 2:
            category = cells[0].get_text(strip=True)
            price = cells[1].get_text(strip=True)
            values.append(
                {
                    "category": category,
                    "price": price,
                },
            )

    return {"price_list": values}
