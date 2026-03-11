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

from fastapi import HTTPException
from loguru import logger


class CustomHttpException(HTTPException):
    """Custom exception class to handle HTTP exceptions with specific details.

    Attributes:
        status_code: The HTTP status code to be returned in the response.
        detail: A message providing details about the error.
    """

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(status_code=status_code, detail=detail)


def handle_internal_error(exception: Exception) -> CustomHttpException:
    """Handles internal server errors by logging the error and raising a custom exception.

    Args:
        exception: The caught exception that triggered the internal error handling.

    Returns:
        An instance of CustomHttpException with a status code of 500.
    """
    logger.error(f"Internal error: {exception}")
    return CustomHttpException(status_code=500, detail="An internal error occurred.")
