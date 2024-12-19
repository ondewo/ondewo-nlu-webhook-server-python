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
from ondewo.logging.logger import logger_console as log  # type: ignore


class CustomHttpException(HTTPException):
    """
    Custom exception class to handle HTTP exceptions with specific details.

    This class extends FastAPI's `HTTPException` to enable customized error handling
    in API responses. It allows specifying both the status code and a detail message
    that describes the error.

    Attributes:
        status_code (int): The HTTP status code to be returned in the response.
        detail (str): A message providing details about the error.
    """

    def __init__(self, status_code: int, detail: str):
        """
        Initializes a new instance of CustomHttpException.

        Args:
            status_code (int): The HTTP status code for the exception (e.g., 404 for Not Found).
            detail (str): A detailed message describing the error that occurred.

        Example:
            ```python
            raise CustomHttpException(status_code=404, detail="Resource not found.")
            ```
        """
        super().__init__(status_code=status_code, detail=detail)


def handle_internal_error(exception: Exception) -> CustomHttpException:
    """
    Handles internal server errors by logging the error and raising a custom exception.

    This function logs the details of the exception and returns a `CustomHttpException`
    with a 500 status code and a generic internal error message. It centralizes error
    handling in the application to ensure consistent responses for unhandled exceptions.

    Args:
        exception (Exception): The caught exception that triggered the internal error handling.

    Returns:
        CustomHttpException: An instance of `CustomHttpException` with a status code of 500
        and a detail message indicating an internal error.

    Example:
        ```python
        try:
            # Code that may raise an exception
        except Exception as caught_exception:
            raise handle_internal_error(caught_exception)
        ```
    """
    log.error(f"Internal error: {exception}")
    return CustomHttpException(status_code=500, detail="An internal error occurred.")
