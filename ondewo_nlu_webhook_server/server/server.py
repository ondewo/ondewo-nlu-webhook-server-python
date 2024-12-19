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
import argparse
import json
import os
import sys
from json import JSONDecodeError
from typing import (
    Dict,
    List,
    Tuple,
)

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Request,
)
from fastapi.security import (
    HTTPBasic,
    HTTPBasicCredentials,
    OAuth2PasswordBearer,
)
from ondewo.logging.decorators import Timer
from ondewo.logging.logger import logger_console as log
from pydantic_core import ValidationError
from starlette import status
from starlette.middleware.cors import CORSMiddleware  # type:ignore

from ondewo_nlu_webhook_server.constants import CALL_CASES
from ondewo_nlu_webhook_server.globals import WebhookGlobals
from ondewo_nlu_webhook_server.server.base_models import (
    WebhookRequest,
    WebhookResponse,
)
from ondewo_nlu_webhook_server.server.relay import call_custom_code
from ondewo_nlu_webhook_server.version import __version__

welcome_message: str = "Welcome from ondewo-nlu-webhook-server-python! If you see this message, your webhook is active."
app = FastAPI()

# region: CORS middleware: used for local debugging to prevent CORS errors
app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=["*"],  # Allow all origins (use specific origins in production)
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Restrict to necessary methods
    allow_headers=["*"],  # Allow all headers
)
# endregion: CORS middleware

# region security: Bearer authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_token(token: str = Depends(oauth2_scheme)) -> str:
    if token != WebhookGlobals.ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_BEARER:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


# endregion security: Bearer authentication

# region security: Http Basic authentication
security = HTTPBasic()


def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)) -> HTTPBasicCredentials:
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

@app.post("/{call_case}", response_model=WebhookResponse)
@Timer(logger=log.debug, log_arguments=True, message='call_case. Elapsed time: {:.5f}')
async def call_case(
    call_case: str,
    request: Request,
    # NOTE: activate token or http basic credentials authentication
    # token: str = Depends(verify_token),  # type: ignore
    credentials: HTTPBasicCredentials = Depends(verify_credentials),  # type:ignore
) -> WebhookResponse:
    """
    Handles HTTP POST requests sent to [server_address]/<call_case>.

    This endpoint processes the incoming messages based on the specified `call_case` parameter
    and returns a corresponding response in JSON format. The processing of the request
    depends on the `call_case` value and is managed accordingly. Both Basic Authentication
    and token verification are required to access this endpoint.

    **Message Handling**:
    - Messages are expected to be in JSON format.
    - If `print_active` is set to `True`, both received and response messages will be logged.

    **Authentication**:
    - The endpoint requires HTTP Basic Authentication. The `username` and `password`
      must be provided in the `Authorization` header.
    - Additionally, a valid token is required to access the endpoint, which is passed
      through the `token` parameter. (Currently uses `verify_token` for validation).

    Args:
        call_case (str): The processing type to be performed, where:
            - `"slot_filling"`: Sends parameter values back to `ondewo-cai`.
            - `"response_refinement"`: Refines the fulfillment messages.
        request (Request): The request object containing the body of the message to be processed.
        token (str, optional): A token for request verification. (Currently uses `verify_token`).
        credentials (HTTPBasicCredentials, optional): Basic authentication credentials for user validation.

    Returns:
        WebhookResponse: A JSON object with the following structure:
            - **fulfillmentText**: Text of the fulfillment message (currently unused by `ondewo-cai`).
            - **fulfillmentMessages**: A list of response messages for the detected intent.
            - **source**: A string passed directly to `QueryResult.webhook_source` of `ondewo-cai`.
            - **payload**: A dictionary passed directly to `QueryResult.webhook_payload` of `ondewo-cai`.
            - **outputContexts**: List of active contexts that the agent is aware of.
            - **followupEventInput**: (Currently unused).

    Example:
        If `call_case` is `"slot_filling"`, the response may include a message such as:
        ```json
        {
            "fulfillmentText": "Please provide your name.",
            "fulfillmentMessages": [{"text": {"text": ["Please provide your name."]}}],
            "source": "ondewo-cai",
            "payload": {},
            "outputContexts": [{"name": "contexts/active", "lifespanCount": 5}],
            "followupEventInput": null
        }
        ```

    **Error Handling**:
    - If an invalid `call_case` is provided, or if an internal error occurs, a 400 or 500 HTTP response will be
      returned, depending on the error type.
    - If authentication fails (either Basic Authentication or token verification), a 401 Unauthorized response
      will be returned.
    """
    if call_case not in CALL_CASES:
        raise HTTPException(status_code=400, detail=f"Unknown call_case: {call_case}")

    request_json: Dict

    try:
        request_json = await request.json()
        log.debug(f"server.py: call_case: webhook_request={request_json}")
    except JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")

    webhook_request: WebhookRequest
    if isinstance(request_json, str):
        # ondewo-nlu-cai sends the request as a string hence we need to load it
        request_json_loaded: Dict = json.loads(request_json)
        try:
            webhook_request = WebhookRequest(**request_json_loaded)
        except ValidationError:
            raise HTTPException(status_code=400, detail="Invalid request format")
    else:
        # ondewo-aim sends the request as a json payload
        try:
            webhook_request = WebhookRequest(**request_json)
        except ValidationError:
            raise HTTPException(status_code=400, detail="Invalid request format")

    # get the webhook request object form the fastapi request
    if not WebhookRequest.model_validate(webhook_request):
        raise HTTPException(status_code=400, detail="Invalid WebhookRequest format")

    # set headers of request into the WebhookRequest object
    webhook_request.headers = dict(request.headers)

    webhook_response: WebhookResponse = webhook_request.extract_webhook_response()

    intent_display_name = webhook_request.queryResult.intent.displayName
    session_id = webhook_request.session
    log.debug(f"server.py: call_case: session_id={session_id} and intent_display_name={intent_display_name}")

    webhook_response = await call_custom_code(
        webhook_request=webhook_request,
        webhook_response=webhook_response,
        call_case=call_case,
    )

    if not WebhookResponse.model_validate(webhook_response):
        raise HTTPException(status_code=500, detail="Invalid response format")

    return webhook_response


# async def index(_: str = Depends(get_current_user)) -> Dict[str, str]:
@app.get("/")
@Timer(logger=log.debug, log_arguments=False, message='index. Elapsed time: {:.5f}')
async def index() -> Dict[str, str]:
    """
    Provides a welcome message when accessing the root endpoint.
    """
    return {"message": welcome_message}


@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    # Update system path to include the parent directory
    sys.path.append(os.path.abspath(os.path.join(__file__, "../..")))

    # Set up argument parser
    parser = argparse.ArgumentParser(description="ONDEWO NLU Webhook Server")

    parser.add_argument(
        "-p",
        "--port",
        help="Port of the ONDEWO NLU Webhook Server.",
        default=int(os.getenv("ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SERVER_PORT", "8000")),
        type=int,
        required=False,
    )
    parser.add_argument(
        "-ht",
        "--host",
        help="Host of the ONDEWO NLU Webhook Server.",
        default=os.getenv("ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SERVER_HOST", "0.0.0.0"),
        required=False,
    )

    # Display startup information
    info_string = (
        "\n\n\n Welcome to ... \n\n"
        "-----------------------------------------------------------------\n"
        "--- ONDEWO NLU Webhook Server Python ---\n"
        f"--- Version: {__version__} ---\n"
        "-----------------------------------------------------------------\n"
    )
    log.debug(info_string)

    # Print environment variables
    try:
        env_string = (
            "\n"
            "----------------------------------------------------------\n"
            "------------------------ ENVIRONMENT ---------------------\n"
            "----------------------------------------------------------\n"
        )
        env_items: List[Tuple[str, str]] = sorted(os.environ.items(), key=lambda environment: environment[0])
        for key, value in env_items:
            env_string += f"{key}={value}\n"
        env_string += (
            "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n"
            "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n"
            "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n"
        )
        log.debug(f"ENVIRONMENT: Environment variables:\n{env_string}")

    except Exception as e:
        log.error(f"ENVIRONMENT: Could not print environment variables! Exception: {e}")

    # Parse command-line arguments
    args = parser.parse_args()

    # Start the server
    import uvicorn

    uvicorn.run("server:app", host=args.host, port=args.port, reload=True)
