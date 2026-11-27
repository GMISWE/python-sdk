import unittest
from unittest.mock import Mock, patch

import requests

from gmicloud._internal._client._http_client import HTTPClient
from gmicloud._internal._exceptions import APIError


class TestHTTPClient(unittest.TestCase):

    def setUp(self):
        self.client = HTTPClient("https://example.invalid")

    @patch("gmicloud._internal._client._http_client.requests.request")
    def test_request_errors_without_response_raise_api_error(self, mock_request):
        for error in (
            requests.ConnectionError("connection refused"),
            requests.Timeout("request timed out"),
            ValueError("invalid request"),
        ):
            with self.subTest(error=type(error).__name__):
                mock_request.side_effect = error
                with self.assertRaises(APIError) as context:
                    self.client.get("/test")
                self.assertEqual(str(context.exception), f"HTTP Request failed: {error}")
                self.assertIs(context.exception.__cause__, error)

    @patch("gmicloud._internal._client._http_client.requests.request")
    def test_request_error_with_response_keeps_status(self, mock_request):
        response = Mock(status_code=200, text="response")
        response.raise_for_status.side_effect = requests.HTTPError("HTTP error")
        mock_request.return_value = response
        with self.assertRaises(APIError) as context:
            self.client.get("/test")
        self.assertEqual(str(context.exception), "HTTP Request failed: 200 - HTTP error")

    @patch("gmicloud._internal._client._http_client.requests.request")
    def test_invalid_error_response_keeps_status_and_body(self, mock_request):
        response = Mock(status_code=502, text="not JSON")
        response.json.side_effect = ValueError("invalid JSON")
        mock_request.return_value = response
        with self.assertRaises(APIError) as context:
            self.client.get("/test")
        self.assertEqual(str(context.exception), "Failed to parse JSON response: 502 - not JSON")
