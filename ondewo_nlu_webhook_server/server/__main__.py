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

import uvicorn
import argparse
import os
import sys
from typing import (
    List,
    Tuple,
)

from fastapi import (
    FastAPI,
)
from ondewo.logging.logger import logger_console as log
from starlette.middleware.cors import CORSMiddleware  # type:ignore

from ondewo_nlu_webhook_server.server.server import router as server_router
from ondewo_nlu_webhook_server.version import __version__

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

# Add routers here
app.include_router(server_router)

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

uvicorn.run("main:app", host=args.host, port=args.port, reload=False)
