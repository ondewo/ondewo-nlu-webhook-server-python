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
import argparse
import os
import sys
import time
from multiprocessing import cpu_count
from signal import (
    SIGINT,
    SIGTERM,
    signal,
)
from types import FrameType

import uvicorn
from fastapi import (
    FastAPI,
)
from loguru import logger
from starlette.middleware.cors import (
    CORSMiddleware,  # type: ignore
)

from ondewo_nlu_webhook_server.server.server import router as server_router
from ondewo_nlu_webhook_server.version import __version__


app: FastAPI = FastAPI()

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


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments with default fallbacks."""
    start_time: float = time.perf_counter()
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="ONDEWO NLU Webhook Server")
    parser.add_argument(
        "-p",
        "--port",
        help="Port of the ONDEWO NLU Webhook Server.",
        default=int(os.getenv("ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SERVER_PORT", "59001")),
        type=int,
    )
    parser.add_argument(
        "-ht",
        "--host",
        help="Host of the ONDEWO NLU Webhook Server.",
        default=os.getenv("ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SERVER_HOST", "0.0.0.0"),
    )

    result: argparse.Namespace = parser.parse_args()
    end_time: float = time.perf_counter()
    logger.info(f"__main__.py: parse_arguments: Elapsed time: {end_time - start_time:.5f}")
    return result


def graceful_shutdown(signal_received: int, frame: FrameType | None) -> None:
    """Handle shutdown signals.

    Args:
        signal_received: The signal received (e.g., SIGINT, SIGTERM).
        frame: The current stack frame (can be None).
    """
    start_time: float = time.perf_counter()
    logger.info(f"Shutdown signal {signal_received} received. Cleaning up ...")
    end_time: float = time.perf_counter()
    logger.info(f"__main__.py: graceful_shutdown: Elapsed time: {end_time - start_time:.5f}")
    sys.exit(0)


def main() -> None:
    start_time: float = time.perf_counter()

    # region Welcome message
    info_string: str = (
        "\n\n\n Welcome to ... \n\n"
        "-----------------------------------------------------------------\n"
        "--- ONDEWO NLU Webhook Server Python ---\n"
        f"--- Version: {__version__} ---\n"
        "-----------------------------------------------------------------\n"
    )
    logger.debug(info_string)
    # endregion Welcome message

    # region: Print environment variables
    try:
        env_string: str = (
            "\n"
            "----------------------------------------------------------\n"
            "------------------------ ENVIRONMENT ---------------------\n"
            "----------------------------------------------------------\n"
        )
        env_items: list[tuple[str, str]] = sorted(os.environ.items(), key=lambda environment: environment[0])
        for key, value in env_items:
            env_string += f"{key}={value}\n"
        env_string += (
            "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n"
            "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n"
            "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n"
        )
        logger.debug(f"ENVIRONMENT: Environment variables:\n{env_string}")

    except Exception as e:
        logger.error(f"ENVIRONMENT: Could not print environment variables! Exception: {e}")
    # endregion: Print environment variables

    # region Parse command-line arguments
    try:
        args: argparse.Namespace | object = parse_arguments()
    except SystemExit:

        class DefaultArgs:
            host: str = str(os.getenv("ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SERVER_HOST", "0.0.0.0"))
            port: int = int(os.getenv("ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_SERVER_PORT", "59001"))

        args = DefaultArgs()
    # endregion Parse command-line arguments

    # region Log environment variables
    try:
        env_items_log: list[tuple[str, str]] = sorted(os.environ.items(), key=lambda x: x[0])
        logger.debug("Environment Variables:\n" + "\n".join(f"{k}={v}" for k, v in env_items_log))
    except Exception as e:
        logger.error(f"Failed to log environment variables: {e}")
    # endregion Log environment variables

    # Handle shutdown signals
    signal(SIGINT, graceful_shutdown)
    signal(SIGTERM, graceful_shutdown)

    # Number of workers based on environment variable. If not set then set workers based on CPU cores
    workers: int = int(os.getenv("ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_NR_OF_WORKERS", cpu_count() * 2 + 1))

    end_time: float = time.perf_counter()
    logger.info(f"__main__.py: main: Elapsed time: {end_time - start_time:.5f}")

    # Start the server
    try:
        uvicorn.run(
            app="ondewo_nlu_webhook_server.server.__main__:app",
            host=args.host,  # type: ignore[union-attr]
            port=args.port,  # type: ignore[union-attr]
            reload=False,
            log_level="info",
            workers=workers,
            access_log=False,
        )
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
