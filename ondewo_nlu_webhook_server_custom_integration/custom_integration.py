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
    slot filling can be used to supply ondewo-cai with additional parameters or modify existing ones before user prompts
    are activated

    2) response refinement
        # request sent to [server_IP]/response_refinement
        # see response_refinement()
        # parameter values cannot be changed
    last minute check can be used to overhaul the fulfillment messages that were generated when all parameters were
    already supplied

Intents where either slot_filling() or response_refinement() are used need to be supplied to the list <active_intents>
    for the custom code to be called. Either the displayName or the intent ID need to be in the list.

"""
from enum import Enum
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
)

from ondewo.logging.decorators import Timer
from ondewo.logging.logger import logger_console as log

from ondewo_nlu_webhook_server.server.base_models import (
    Context,
    Intent,
)
from ondewo_nlu_webhook_server_custom_integration.utils.helpers import replace_placeholder_in_text


# region Intent Mapping
class IntentMapping(Enum):
    DEFAULT_EXIT_INTENT = "Default Exit Intent"  # 765bb30a-4775-4171-9cc6-72d3cb64cff7
    DEFAULT_FALLBACK_INTENT = "Default Fallback Intent"  # e0667758-0f61-5c0e-9575-47341b58bd8f
    DEFAULT_RESET_INTENT = "Default Reset Intent"  # 7801a7a2-2b50-53ba-96f9-b79b596b2779
    DEFAULT_WELCOME_INTENT = "Default Welcome Intent"  # d420ff8b-8b71-41f0-9b2d-1eabcffec1ae

    ###########################################################
    # TODO: Define here your intent display names variables
    ###########################################################
    I_EXAMPLE_MY_DATE = "i.example_my-date"
    I_EXAMPLE_THANKS_GOOD = "i.example_thanks_good"
    I_EXAMPLE_WEBREQUEST = "i.example_webrequest"


# endregion Intent Mapping

# region CASE 1: Slot Filling

@Timer(logger=log.debug, log_arguments=True, message='slot_filling. Elapsed time: {:.5f}')
async def slot_filling(
    active_intent: Intent,
    active_contexts: Optional[List[Context]] = None,
    headers: Optional[Dict[str, str]] = None,
) -> Optional[List[Context]]:
    """
    slot_filling() is called when the request was posted to [server-IP]/slot_filling and
        the detected intent is found in the <active_intents> list
    <response> holds a copy of the request message from ondewo-cai
    <headers> holds the header(s) sent with the request

    Changes that can be accomplished here:
        changing parameter values globally or context-specifically
        changing active contexts

    Args:
        headers: list of headers of the request message
        active_intent: Intent object with intent.displayName and intent.name (intent ID)
        active_contexts: list of active <Context> objects
            <Context> attributes:
                .name (str)
                .lifespanCount (int)
                .parameters (dict)

    Returns: active contexts (list of <Context> objects) and their parameters

    """

    """
    ################################
    ######## YOUR CODE HERE ########
    ################################

    # Example: list active context names
    name_list = []
    for context in active_contexts:
        name_list.append(context.name)

    # Example: change parameter "amount" of first context
    active_contexts[0].parameters["amount"] = 10


    # Example: add an empty Context:

    from custom_code_helpers.helpers import create_new_context_name
    new_context_name = create_new_context_name(active_contexts, "my-new-context-99")
    active_contexts.append(
        Context(
            name=new_context_name,
            lifespanCount=10,
            parameters={}
        )
    )
    """
    if active_intent.displayName in {IntentMapping.DEFAULT_WELCOME_INTENT.value}:  # TODO: Example Intent, use yours
        log.debug(f"slot_filling: Intent handler called for intent display name '{active_intent.displayName}'")

    elif active_intent.displayName in {IntentMapping.I_EXAMPLE_THANKS_GOOD.value}:  # TODO: Example Intent, use yours
        log.debug(f"slot_filling: Intent handler called for intent display name '{active_intent.displayName}'")

    elif active_intent.displayName in {IntentMapping.I_EXAMPLE_MY_DATE.value}:  # TODO: Example Intent, use yours
        log.debug(f"slot_filling: Intent handler called for intent display name '{active_intent.displayName}'")

    else:
        log.debug(f"slot_filling: No handler for intent display name '{active_intent.displayName}'")

    return active_contexts


# endregion CASE 1: Slot Filling

# region CASE 2: Response Refinement

@Timer(logger=log.debug, log_arguments=True, message='response_refinement. Elapsed time: {:.5f}')
async def response_refinement(
    headers: Dict[str, str],
    active_intent: Intent,
    fulfillment_messages: List[Dict[str, Any]],
    active_contexts: Optional[List[Context]],
    parameters: Optional[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], Optional[List[Context]]]:
    """
    response_refinement() is called when the request was posted to [server-IP]/response_refinement and
        the detected intent is found in the <active_intents> list

    Changes that can be accomplished here:
        changes to fulfillment messages
    Changes that cannot be accomplished here:
        changes to active active_contexts
        changes to parameter values

    Active active_contexts and global parameters are provided in case their values are needed for a newly constructed message.

    Args:
        headers: list of headers sent with the request
        active_intent: Intent object with intent.displayName and intent.name (intent ID)
        fulfillment_messages: list of fulfillment messages (dicts), messages can be structured in various ways
        active_contexts: list of active <Context> objects
            <Context> attributes:
                .name (str)
                .lifespanCount (int)
                .parameters (dict)

    Returns:
        List[Dict[str, Any]]: A list of refined fulfillment messages.
    """
    """
    ################################
    ######## YOUR CODE HERE ########
    ################################

    Example: add text message

    from custom_code_helpers.helpers import add_text_to_fulfillment
    fulfillment_messages = add_text_to_fulfillment(fulfillment_messages, "response text added by webhook server")


    Example: override text with completely new message

    from custom_code_helpers.helpers import override_fulfillment_with_text
    fulfillment_messages = override_fulfillment_with_text(
        fulfillment_messages,
        "response text override by webhook server"
    )
    """
    if active_intent.displayName in {IntentMapping.DEFAULT_WELCOME_INTENT.value}:
        log.debug(f"response_refinement: Intent handler called for intent display name '{active_intent.displayName}'")

    elif active_intent.displayName in {IntentMapping.I_EXAMPLE_THANKS_GOOD.value}:  # TODO: Example Intent, use yours
        log.debug(f"response_refinement: Intent handler called for intent display name '{active_intent.displayName}'")

    elif active_intent.displayName in {IntentMapping.I_EXAMPLE_WEBREQUEST.value}:  # TODO: Example Intent, use yours
        fulfillment_messages = replace_placeholder_in_text(
            fulfillment_messages=fulfillment_messages,
            replace_text="<EXAMPLE_PLACEHOLDER>",  # TODO: Example placeholder, use yours
            active_intent=active_intent,
            parameters=parameters,
        )
    elif active_intent.displayName in {IntentMapping.DEFAULT_FALLBACK_INTENT.value}:
        # IDEA: possible request to LLM or RAG system
        pass

    else:
        log.debug(f"response_refinement: No handler for intent display name '{active_intent.displayName}'")

    return fulfillment_messages, active_contexts

# endregion CASE 2: Response Refinement
