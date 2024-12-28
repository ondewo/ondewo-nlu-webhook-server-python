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

from typing import (
    Any,
    Dict,
    List,
    Optional,
    Union,
)

import httpx
from fastapi import HTTPException


async def make_http_request(
    method: str,
    url: str,
    headers: Dict[str, str],
    params: Optional[Dict[str, Any]] = None,
    json_payload: Optional[Dict[str, Union[str, int, float, bool, Dict, list]]] = None,
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Makes an asynchronous HTTP request using the specified method, URL, headers, and optional parameters or
    JSON payload.

    Args:
        method (str): The HTTP method to use (e.g., 'GET', 'POST', 'DELETE', 'PUT').
        url (str): The URL endpoint to send the request to.
        headers (Dict[str, str]): Headers to include in the request, such as authorization tokens.
        params (Optional[Dict[str, Union[str, int, float, bool]]], optional): URL query parameters to include in
        the request. Defaults to None.
        json_payload (Optional[Dict[str, Union[str, int, float, bool, Dict, list]]], optional): JSON payload for
        POST or PUT requests. Defaults to None.

    Returns:
        Dict[str, Union[str, int, float, bool, Dict, list]]: The JSON-parsed response content if the request is
        successful (status code 200 or 201).

    Raises:
        HTTPException: If the server returns an error status code (other than 200 or 201) or if the response
        cannot be parsed as JSON.
    """
    async with httpx.AsyncClient() as client:
        # Determine the HTTP method and make the request
        if method.lower() == "post":
            if json_payload is None:
                # POST request without a JSON payload
                response = await client.post(url, headers=headers, params=params)
            elif params is None:
                # POST request without params
                response = await client.post(url, data=json_payload, headers=headers)
            else:
                # POST request with a JSON payload
                response = await client.post(url, json=json_payload, params=params)
        elif method.lower() == "get":
            # GET request
            response = await client.get(url, headers=headers, params=params)
        elif method.lower() == "delete":
            # DELETE request
            response = await client.delete(url, headers=headers, params=params)
        elif method.lower() == "put":
            # PUT request with JSON payload, if applicable
            response = await client.put(
                url, headers=headers, params=params, json=json_payload,
            )
        else:
            # Raise an exception if an unsupported method is provided
            raise HTTPException(status_code=405, detail=f"Unsupported HTTP method: {method}")

        # Check if the response is successful (status codes 200 or 201)
        if response.status_code in {200, 201}:
            try:
                # Attempt to parse the response as JSON and return it
                return response.json()  # type:ignore
            except ValueError:
                # Raise an exception if the response body is not valid JSON
                raise HTTPException(
                    status_code=500, detail="Invalid JSON response from server.",
                )
        else:
            # Raise an exception for unsuccessful responses, including the status code and server message
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed request with status: {response.status_code}, message: {response.text}",
            )
