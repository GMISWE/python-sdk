import logging

import requests
from .._exceptions import APIError
from .._exceptions import UnauthorizedError
from .._constants import *

logger = logging.getLogger(__name__)


class HTTPClient:
    """
    A simple HTTP API client for interacting with REST APIs.
    """

    def __init__(self, base_url):
        """
        Initialize the HTTP client.

        :param base_url: The base URL of the REST API (e.g., https://api.example.com)
        """
        self.base_url = base_url.rstrip('/')

    def _prepare_url(self, endpoint):
        """
        Helper method to prepare the full URL.

        :param endpoint: The API endpoint to append to the base URL.
        :return: The full API URL as a string.
        """
        return f"{self.base_url}{endpoint}"

    def _send_request(self, method, endpoint, custom_headers=None, data=None, params=None):
        """
        Internal method for sending HTTP requests.

        :param method: The HTTP method (e.g., 'GET', 'POST', 'PUT', 'PATCH', 'DELETE').
        :param endpoint: The API endpoint.
        :param custom_headers: The request headers (optional).
        :param data: The request payload for POST/PUT/PATCH requests (optional).
        :param params: The query parameters for GET/DELETE requests (optional).
        :return: The JSON response parsed as a Python dictionary.
        :raises APIError: If the request fails or the response is invalid.
        """
        url = self._prepare_url(endpoint)
        headers = {
            ACCEPT_HEADER: JSON_CONTENT_TYPE,
            CONTENT_TYPE_HEADER: JSON_CONTENT_TYPE,
        }

        # Add custom headers if provided
        if custom_headers:
            headers.update(custom_headers)

        response = None
        try:
            response = requests.request(method, url, params=params, json=data, headers=headers)
            logger.debug(response.text)
            if response.status_code == 401:
                raise UnauthorizedError("Access token expired or invalid.")
            elif response.status_code != 200 and response.status_code != 201:
                if url.find("ie/artifact") != -1 or url.find("ie/task") != -1:
                    error_message = response.json().get('error', 'Unknown error')
                else:
                    error_message = response.json().get('message', 'Unknown error')
                raise APIError(f"HTTP Request failed: {error_message}")
            # Raise for HTTP errors
            response.raise_for_status()

        except requests.exceptions.RequestException as e:
            raise APIError(f"HTTP Request failed: {str(e)}")
        except ValueError as e:
            # Fallback if response JSON is invalid
            raise APIError(f"Failed to parse JSON response: {response.text}")

        if response.headers.get(CONTENT_TYPE_HEADER).find(JSON_CONTENT_TYPE) != -1:
            return response.json()
        elif response.headers.get(CONTENT_TYPE_HEADER).find(TEXT_CONTENT_TYPE) != -1:
            raise APIError(f"Got text response: {response.text}")
        else:
            raise APIError(f"Unsupported content type: {response.headers.get(CONTENT_TYPE_HEADER)}")

    def post(self, endpoint, custom_headers=None, data=None):
        """
        Send a POST request to the given API endpoint.

        :param endpoint: The API endpoint.
        :param custom_headers: The request headers (optional).
        :param data: The request payload as a dictionary.
        :return: The JSON response parsed as a Python dictionary.
        """
        return self._send_request(method=HTTP_METHOD_POST, endpoint=endpoint, custom_headers=custom_headers, data=data)

    def get(self, endpoint, custom_headers=None, params=None):
        """
        Send a GET request to the given API endpoint.

        :param endpoint: The API endpoint.
        :param custom_headers: The request headers (optional).
        :param params: Query parameters as a dictionary (optional).
        :return: The JSON response parsed as a Python dictionary.
        """
        return self._send_request(method=HTTP_METHOD_GET, endpoint=endpoint, custom_headers=custom_headers,
                                  params=params)

    def put(self, endpoint, custom_headers=None, data=None):
        """
        Send a PUT request to the given API endpoint.

        :param endpoint: The API endpoint.
        :param custom_headers: The request headers (optional).
        :param data: The request payload as a dictionary.
        :return: The JSON response parsed as a Python dictionary.
        """
        return self._send_request(method=HTTP_METHOD_PUT, endpoint=endpoint, custom_headers=custom_headers, data=data)

    def patch(self, endpoint, custom_headers=None, data=None):
        """
        Send a PATCH request to the given API endpoint.

        :param endpoint: The API endpoint.
        :param custom_headers: The request headers (optional).
        :param data: The request payload as a dictionary.
        :return: The JSON response parsed as a Python dictionary.
        """
        return self._send_request(method=HTTP_METHOD_PATCH, endpoint=endpoint, custom_headers=custom_headers, data=data)

    def delete(self, endpoint, custom_headers=None, params=None):
        """
        Send a DELETE request to the given API endpoint.

        :param endpoint: The API endpoint.
        :param custom_headers: The request headers (optional).
        :param params: Query parameters as a dictionary (optional).
        :return: The JSON response parsed as a Python dictionary.
        """
        return self._send_request(method=HTTP_METHOD_DELETE, endpoint=endpoint, custom_headers=custom_headers,
                                  params=params)
