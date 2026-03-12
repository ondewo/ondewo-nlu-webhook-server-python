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
This is a template script for
    1) setting up a local server for webhook calls
    2) process json-formatted POST-messages sent to [local IP + port]/slot_filling & /response_refinement
        from ondewo-cai
    3) return a json-formatted message back to ondewo-cai

A request is sent by ondewo-cai when an intent is matched where a webhook call is activated

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! Any logic should be added in CUSTOM_CODE.py !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

If server.py is called directly, it will create the server using flask itself with debugging activated.
This is not recommended for production
"""

import json
import time
from json import JSONDecodeError
from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
)
from fastapi.security import (
    HTTPBasic,
    HTTPBasicCredentials,
    OAuth2PasswordBearer,
)
from loguru import logger
from pydantic_core import ValidationError
from starlette import status

from ondewo_nlu_webhook_server.constants import CALL_CASES
from ondewo_nlu_webhook_server.globals import WebhookGlobals
from ondewo_nlu_webhook_server.server.base_models import (
    EventInput,
    WebhookRequest,
    WebhookResponse,
)
from ondewo_nlu_webhook_server.server.relay import call_custom_code
from ondewo_nlu_webhook_server.version import __version__


router: APIRouter = APIRouter()

# welcome message
welcome_message: str = (
    f"Welcome to ONDEWO NLU Webhook Server Python {__version__}! "
    "GitHub: https://github.com/ondewo/ondewo-nlu-webhook-server-python"
)

# region security: Bearer authentication
oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="token")


def verify_token(token: Any = Depends(oauth2_scheme)) -> str:  # type: ignore[assignment]
    if token != WebhookGlobals.ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_BEARER:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


# endregion security: Bearer authentication

# region security: Http Basic authentication
security: HTTPBasic = HTTPBasic()


def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)) -> HTTPBasicCredentials:  # type: ignore[assignment]
    if (
        credentials.username != WebhookGlobals.ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_HTTP_BASIC_AUTH_USERNAME
        or credentials.password != WebhookGlobals.ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_HTTP_BASIC_AUTH_PASSWORD
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials


# endregion security: Http Basic authentication


@router.post("/{call_case}", response_model=WebhookResponse)
async def call_case(
    call_case: str,
    request: Request,
    # NOTE: activate token or http basic credentials authentication
    # token: str = Depends(verify_token),
    credentials: HTTPBasicCredentials = Depends(verify_credentials),  # type: ignore[assignment]
) -> WebhookResponse:
    """Handles HTTP POST requests sent to [server_address]/<call_case>.

    Args:
        call_case: The processing type ("slot_filling" or "response_refinement").
        request: The request object containing the body of the message.
        credentials: Basic authentication credentials for user validation.

    Returns:
        WebhookResponse with fulfillment data.
    """
    start_time: float = time.perf_counter()

    if call_case not in CALL_CASES:
        raise HTTPException(status_code=400, detail=f"Unknown call_case: {call_case}")

    request_json: dict | str

    try:
        request_json = await request.json()
        logger.debug(f"server.py: call_case: webhook_request={request_json}")
    except JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")

    webhook_request: WebhookRequest
    if isinstance(request_json, str):
        request_json_loaded: dict = json.loads(request_json)
        try:
            webhook_request = WebhookRequest(**request_json_loaded)
        except ValidationError, TypeError:
            raise HTTPException(status_code=400, detail="Invalid request format")
    else:
        try:
            webhook_request = WebhookRequest(**request_json)
        except ValidationError, TypeError:
            raise HTTPException(status_code=400, detail="Invalid request format")

    webhook_request.headers = dict(request.headers)

    webhook_response: WebhookResponse = WebhookResponse(
        fulfillmentText=webhook_request.queryResult.fulfillmentText,
        fulfillmentMessages=(
            webhook_request.queryResult.fulfillmentMessages if webhook_request.queryResult.fulfillmentMessages else []
        ),
        source="",
        payload={},
        outputContexts=webhook_request.queryResult.outputContexts,
        followupEventInput=EventInput(),
    )

    intent_display_name: str = webhook_request.queryResult.intent.displayName
    session_id: str = webhook_request.session
    logger.debug(f"server.py: call_case: session_id={session_id} and intent_display_name={intent_display_name}")

    webhook_response = await call_custom_code(
        webhook_request=webhook_request,
        webhook_response=webhook_response,
        call_case=call_case,
    )

    logger.debug(
        f"webhook_response.model_dump_json(): {json.dumps(webhook_response.model_dump(), indent=2)}",
    )

    end_time: float = time.perf_counter()
    logger.debug(f"server.py: call_case: Elapsed time: {end_time - start_time:.5f}")
    return webhook_response


@router.get("/")
async def index() -> dict[str, str]:
    """Provides a welcome message when accessing the root endpoint."""
    start_time: float = time.perf_counter()
    result: dict[str, str] = {"message": welcome_message}
    end_time: float = time.perf_counter()
    logger.debug(f"server.py: index: Elapsed time: {end_time - start_time:.5f}")
    return result


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
