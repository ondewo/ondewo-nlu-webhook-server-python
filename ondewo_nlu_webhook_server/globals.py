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

import os
from dataclasses import dataclass
from typing import ClassVar


@dataclass
class WebhookGlobals():

    ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SERVER_HOST: ClassVar[str] = str(
        os.getenv("ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SERVER_HOST", "0.0.0.0").strip(),
    )

    ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SERVER_PORT: ClassVar[int] = int(
        os.getenv("ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SERVER_PORT", "8000").strip(),
    )

    ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_HTTP_BASIC_AUTH_USERNAME: ClassVar[str] = str(
        os.getenv("ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_HTTP_BASIC_AUTH_USERNAME", "").strip(),
    )

    ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_HTTP_BASIC_AUTH_PASSWORD: ClassVar[str] = str(
        os.getenv("ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_HTTP_BASIC_AUTH_PASSWORD", "").strip(),
    )

    ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_BEARER: ClassVar[str] = str(
        os.getenv("ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_BEARER", "").strip(),
    )
