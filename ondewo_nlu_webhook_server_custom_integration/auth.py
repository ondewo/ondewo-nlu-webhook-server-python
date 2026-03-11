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

import json
import os
from typing import (
    Any,
)

import grpc  # type: ignore
from loguru import logger
from ondewo.nlu import intent_pb2
from ondewo.nlu.client import Client as NluClient
from ondewo.nlu.client_config import ClientConfig

from ondewo_nlu_webhook_server.server.base_models import (
    GetIntentRequest,
    LoginRequest,
    LoginResponse,
)


ONDEWO_NLU_CAI_GRPC_CERT: str = os.getenv("ONDEWO_NLU_CAI_GRPC_CERT", "").strip()
ONDEWO_NLU_CAI_HOST: str = os.getenv("ONDEWO_NLU_CAI_HOST", "").strip()
ONDEWO_NLU_CAI_HTTP_BASIC_AUTH_TOKEN: str = os.getenv("ONDEWO_NLU_CAI_HTTP_BASIC_AUTH_TOKEN", "").strip()
ONDEWO_NLU_CAI_PORT: str = os.getenv("ONDEWO_NLU_CAI_PORT", "").strip()
ONDEWO_NLU_CAI_USER_NAME: str = os.getenv("ONDEWO_NLU_CAI_USER_NAME", "").strip()
ONDEWO_NLU_CAI_USER_PASS: str = os.getenv("ONDEWO_NLU_CAI_USER_PASS", "").strip()

ONDEWO_BPI_CAI_MAX_MESSAGE_LENGTH: int = 10 * 1024 * 1024

service_config_json: str = json.dumps(
    {
        "methodConfig": [
            {
                "name": [
                    {},
                ],
                "retryPolicy": {
                    "maxAttempts": 100,
                    "initialBackoff": "0.1s",
                    "maxBackoff": "30s",
                    "backoffMultiplier": 2,
                    "retryableStatusCodes": [
                        grpc.StatusCode.CANCELLED.name,
                        grpc.StatusCode.UNKNOWN.name,
                        grpc.StatusCode.DEADLINE_EXCEEDED.name,
                        grpc.StatusCode.NOT_FOUND.name,
                        grpc.StatusCode.RESOURCE_EXHAUSTED.name,
                        grpc.StatusCode.ABORTED.name,
                        grpc.StatusCode.INTERNAL.name,
                        grpc.StatusCode.UNAVAILABLE.name,
                        grpc.StatusCode.DATA_LOSS.name,
                    ],
                },
            },
        ],
    },
)

options: set[tuple[str, Any]] = {
    ("grpc.max_send_message_length", ONDEWO_BPI_CAI_MAX_MESSAGE_LENGTH),
    ("grpc.max_receive_message_length", ONDEWO_BPI_CAI_MAX_MESSAGE_LENGTH),
    ("grpc.keepalive_time_ms", 2**31 - 1),
    ("grpc.keepalive_timeout_ms", 60000),
    ("grpc.keepalive_permit_without_calls", False),
    ("grpc.http2.max_pings_without_data", 4),
    ("grpc.dns_enable_srv_queries", 1),
    ("grpc.enable_retries", 1),
    ("grpc.service_config", service_config_json),
}

nlu_client_config: ClientConfig = ClientConfig(
    host=ONDEWO_NLU_CAI_HOST,
    port=ONDEWO_NLU_CAI_PORT,
    http_token=ONDEWO_NLU_CAI_HTTP_BASIC_AUTH_TOKEN,
    user_name=ONDEWO_NLU_CAI_USER_NAME,
    password=ONDEWO_NLU_CAI_USER_PASS,
)

nlu_client: NluClient = NluClient(
    config=nlu_client_config,
    use_secure_channel=bool(nlu_client_config.grpc_cert),
    options=options,
)


def login() -> LoginResponse | None:
    """Logs into the ONDEWO NLU service.

    Returns:
        The login response containing the authentication token if successful.

    Raises:
        ValueError: If login fails due to missing or invalid response data.
    """
    logger.info("Attempting to log in.")
    try:
        login_response: LoginResponse = nlu_client.services.users.login(
            request=LoginRequest(  # type: ignore
                userEmail=nlu_client_config.user_name,
                password=nlu_client_config.password,
            ),
        )
        if not login_response or not login_response.authToken:
            raise ValueError("Login response or auth token is missing.")
        logger.info("Login successful.")
        return login_response

    except Exception as login_exception:
        logger.error(f"Login failed: {login_exception}")
        raise


def get_intent() -> intent_pb2.Intent | None:
    """Retrieves intent information from the ONDEWO NLU service.

    Returns:
        The Intent proto if the request is successful, None otherwise.

    Raises:
        Exception: If the API request fails.
    """
    logger.info("Fetching intent information.")
    try:
        nlu_request: GetIntentRequest = GetIntentRequest(
            name="projects/<example_project_id>/agent/intents/<example_intent_name>",
            languageCode="de-DE",
        )
        intent: intent_pb2.Intent = nlu_client.services.intents.get_intent(request=nlu_request)  # type: ignore
        logger.debug(f"Intent response: {intent}")
        logger.info("Successfully fetched intent information.")
        return intent

    except Exception as get_intent_exception:
        logger.error(f"Failed to get intent: {get_intent_exception}")
        return None
