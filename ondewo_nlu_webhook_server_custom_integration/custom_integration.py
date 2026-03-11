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

"""
There are 2 cases for CUSTOM_CODE.py to be executed after a webhook request:

    1) slot filling
        # request sent to [server_IP]/slot_filling
        # see slot_filling()
        # fulfillment messages cannot be changed

    2) response refinement
        # request sent to [server_IP]/response_refinement
        # see response_refinement()
        # parameter values cannot be changed

Intents where either slot_filling() or response_refinement() are used need to be supplied to the list <active_intents>
    for the custom code to be called.
"""

import time
from enum import Enum
from typing import (
    Any,
)

from loguru import logger

from ondewo_nlu_webhook_server.server.base_models import (
    Context,
    Intent,
)
from ondewo_nlu_webhook_server_custom_integration.utils.helpers import replace_placeholder_in_text


# region Intent Mapping
class IntentMapping(Enum):
    DEFAULT_EXIT_INTENT = "Default Exit Intent"
    DEFAULT_FALLBACK_INTENT = "Default Fallback Intent"
    DEFAULT_RESET_INTENT = "Default Reset Intent"
    DEFAULT_WELCOME_INTENT = "Default Welcome Intent"

    ###########################################################
    # TODO: Define here your intent display names variables
    ###########################################################
    I_EXAMPLE_MY_DATE = "i.example_my-date"
    I_EXAMPLE_THANKS_GOOD = "i.example_thanks_good"
    I_EXAMPLE_WEBREQUEST = "i.example_webrequest"


# endregion Intent Mapping

# region CASE 1: Slot Filling


async def slot_filling(
    active_intent: Intent,
    active_contexts: list[Context] | None = None,
    headers: dict[str, str] | None = None,
) -> list[Context] | None:
    """slot_filling() is called when the request was posted to [server-IP]/slot_filling.

    Args:
        headers: list of headers of the request message
        active_intent: Intent object with intent.displayName and intent.name (intent ID)
        active_contexts: list of active <Context> objects

    Returns:
        active contexts (list of <Context> objects) and their parameters
    """
    start_time: float = time.perf_counter()

    if (
        active_intent.displayName in {IntentMapping.DEFAULT_WELCOME_INTENT.value}
        or active_intent.displayName in {IntentMapping.I_EXAMPLE_THANKS_GOOD.value}
        or active_intent.displayName in {IntentMapping.I_EXAMPLE_MY_DATE.value}
    ):
        logger.debug(f"slot_filling: Intent handler called for intent display name '{active_intent.displayName}'")

    else:
        logger.debug(f"slot_filling: No handler for intent display name '{active_intent.displayName}'")

    end_time: float = time.perf_counter()
    logger.debug(f"slot_filling: Elapsed time: {end_time - start_time:.5f}")
    return active_contexts


# endregion CASE 1: Slot Filling

# region CASE 2: Response Refinement


async def response_refinement(
    headers: dict[str, str],
    active_intent: Intent,
    fulfillment_messages: list[dict[str, Any]],
    active_contexts: list[Context] | None,
    parameters: dict[str, Any] | None,
) -> tuple[list[dict[str, Any]], list[Context] | None]:
    """response_refinement() is called when the request was posted to [server-IP]/response_refinement.

    Args:
        headers: list of headers sent with the request
        active_intent: Intent object with intent.displayName and intent.name (intent ID)
        fulfillment_messages: list of fulfillment messages (dicts)
        active_contexts: list of active <Context> objects
        parameters: additional parameters

    Returns:
        Tuple of refined fulfillment messages and active contexts.
    """
    start_time: float = time.perf_counter()

    if active_intent.displayName in {IntentMapping.DEFAULT_WELCOME_INTENT.value} or active_intent.displayName in {
        IntentMapping.I_EXAMPLE_THANKS_GOOD.value,
    }:
        logger.debug(
            f"response_refinement: Intent handler called for intent display name '{active_intent.displayName}'",
        )

    elif active_intent.displayName in {IntentMapping.I_EXAMPLE_WEBREQUEST.value}:
        fulfillment_messages = replace_placeholder_in_text(
            fulfillment_messages=fulfillment_messages,
            replace_text="<EXAMPLE_PLACEHOLDER>",
            active_intent=active_intent,
            parameters=parameters,
        )
    elif active_intent.displayName in {IntentMapping.DEFAULT_FALLBACK_INTENT.value}:
        pass

    else:
        logger.debug(f"response_refinement: No handler for intent display name '{active_intent.displayName}'")

    end_time: float = time.perf_counter()
    logger.debug(f"response_refinement: Elapsed time: {end_time - start_time:.5f}")
    return fulfillment_messages, active_contexts


# endregion CASE 2: Response Refinement
