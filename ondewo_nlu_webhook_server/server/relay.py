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

from copy import deepcopy

from ondewo.logging.decorators import Timer
from ondewo.logging.logger import logger_console as log

from ondewo_nlu_webhook_server.constants import (
    RESPONSE_REFINEMENT_CASE,
    SLOT_FILLING_CASE,
)
from ondewo_nlu_webhook_server.server.base_models import (
    WebhookRequest,
    WebhookResponse,
)
from ondewo_nlu_webhook_server_custom_integration.custom_integration import (
    response_refinement,
    slot_filling,
)


@Timer(
    logger=log.info, log_arguments=False,
    message="relay.py: call_custom_code: Elapsed time: {}",
)
async def call_custom_code(
    webhook_request: WebhookRequest,
    webhook_response: WebhookResponse,
    call_case: str,
) -> WebhookResponse:
    """
    calls functions defined in <CUSTOM_CODE.py> for the defined <call_case>s
    tests is implemented through a specific "ONDEWO_test_webhook_server" entry in the header.keys()

    Args:
        webhook_request: request sent by ondewo-cai
        webhook_response: pre-constructed response (copy of request)
        call_case: "slot_filling" or "response_refinement"

    Returns:
        response object
    """
    try:
        if call_case == SLOT_FILLING_CASE:
            log.debug("relay.py: call_custom_code: slot_filling: START:")
            # get parameters and active_contexts from _custom_code and relay them to the response object
            webhook_response.outputContexts = await slot_filling(
                active_intent=webhook_request.queryResult.intent,
                active_contexts=webhook_request.queryResult.outputContexts,
                headers=webhook_request.headers,
            )
            log.debug(
                "relay.py: call_custom_code: slot_filling: END:"
                f"webhook_response.outputContexts={webhook_response.outputContexts}",
            )

        elif call_case == RESPONSE_REFINEMENT_CASE:
            log.debug("relay.py: call_custom_code: response_refinement: START:")
            webhook_response.fulfillmentMessages, webhook_response.outputContexts = await response_refinement(
                headers=webhook_request.headers,
                active_intent=webhook_request.queryResult.intent,
                fulfillment_messages=webhook_request.queryResult.fulfillmentMessages,
                active_contexts=deepcopy(webhook_request.queryResult.outputContexts),
                parameters=webhook_request.queryResult.parameters,
            )
            log.debug(
                "relay.py: call_custom_code: response_refinement: END: "
                f"fulfillmentMessages={webhook_response} \n"
                f"outputContexts={webhook_response.outputContexts}",
            )

        log.debug("relay.py: call_custom_code: response_refinement: END: ")
        return webhook_response

    except Exception as e:
        log.error(f"Error in call_custom_code: {e}")
        return webhook_response
