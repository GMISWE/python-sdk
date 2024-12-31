import requests
from GMICloud.http_client.exceptions import APIError


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

    def _send_request(self, method, endpoint, token=None, data=None, params=None):
        """
        Internal method for sending HTTP requests.

        :param method: The HTTP method (e.g., 'GET', 'POST').
        :param endpoint: The API endpoint.
        :param token: The authorization token (optional).
        :param data: The request payload for POST/PUT requests (optional).
        :param params: The query parameters for GET requests (optional).
        :return: The JSON response parsed as a Python dictionary.
        :raises APIError: If the request fails or the response is invalid.
        """
        url = self._prepare_url(endpoint)
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }

        # Add Authorization header if token is provided
        if token:
            headers["Authorization"] = token

        try:
            if method == "POST":
                response = requests.post(url, json=data, headers=headers)
            elif method == "GET":
                response = requests.get(url, params=params, headers=headers)
            else:
                raise APIError(f"Unsupported HTTP method: {method}")

            # Raise for HTTP errors
            response.raise_for_status()

        except requests.exceptions.RequestException as e:
            raise APIError(f"HTTP Request failed: {str(e)}")

        # Handle successful responses
        try:
            return response.json()
        except ValueError:
            raise APIError("Failed to parse JSON response")

    def post(self, endpoint, token=None, data=None):
        """
        Send a POST request to the given API endpoint.

        :param endpoint: The API endpoint.
        :param token: The authorization token (optional).
        :param data: The request payload as a dictionary.
        :return: The JSON response parsed as a Python dictionary.
        """
        return self._send_request("POST", endpoint, token=token, data=data)

    def get(self, endpoint, token=None, params=None):
        """
        Send a GET request to the given API endpoint.

        :param endpoint: The API endpoint.
        :param token: The authorization token (optional).
        :param params: Query parameters as a dictionary (optional).
        :return: The JSON response parsed as a Python dictionary.
        """
        return self._send_request("GET", endpoint, token=token, params=params)
