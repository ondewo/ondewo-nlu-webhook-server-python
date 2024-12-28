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

from base64 import b64encode
from typing import (
    Any,
    Dict,
)

import pytest

from ondewo_nlu_webhook_server.globals import WebhookGlobals
from ondewo_nlu_webhook_server.server.base_models import WebhookRequest


@pytest.fixture
def valid_request_data() -> Dict[str, Any]:
    """Fixture for valid request data."""
    webhook_request: WebhookRequest = WebhookRequest.create_sample_request()
    return webhook_request.model_dump()  # type:ignore # serialize to json


@pytest.fixture
def headers() -> Dict[str, str]:
    # Retrieve username and password from WebhookGlobals
    username = WebhookGlobals.ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_HTTP_BASIC_AUTH_USERNAME
    password = WebhookGlobals.ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_HTTP_BASIC_AUTH_PASSWORD

    # Create the HTTP Basic Auth header
    credentials = f"{username}:{password}"
    encoded_credentials = b64encode(credentials.encode('utf-8')).decode('utf-8')

    # Return headers including the Basic Auth header
    return {
        "Authorization": f"Basic {encoded_credentials}",
    }
