import jwt

from ._http_client import HTTPClient
from .._config import IAM_SERVICE_BASE_URL
from .._models import *
from .._constants import CLIENT_ID_HEADER


class IAMClient:
    """
    Client for interacting with the IAM Service API.
    """

    def __init__(self, client_id: str, email: str, password: str):
        """
        Initialize IAMClient with client credentials and an IAMClient instance.

        :param client_id: Client ID for login.
        :param email: Email for login.
        :param password: Password for login.
        """
        self._client_id = client_id
        self._email = email
        self._password = password
        self._access_token = ""
        self._refresh_token = ""
        self._user_id = ""
        self.client = HTTPClient(IAM_SERVICE_BASE_URL)

    def login(self):
        """
        Logs in a user with the given username and password.
        """
        custom_headers = {
            CLIENT_ID_HEADER: self._client_id
        }
        req = LoginRequest(email=self._email, password=self._password)
        result = self.client.post("/me/sessions", custom_headers, req.model_dump())

        resp = LoginResponse.model_validate(result)
        self._access_token = resp.accessToken
        self._refresh_token = resp.refreshToken
        self._user_id = self.parse_user_id()

    def refresh_token(self):
        """
        Refreshes a user's token using a refresh token.
        """
        custom_headers = {
            CLIENT_ID_HEADER: self._client_id
        }
        result = self.client.patch("/me/sessions", custom_headers, {"refreshToken": self.refresh_token})

        resp = LoginResponse.model_validate(result)
        self._access_token = resp.accessToken
        self._refresh_token = resp.refreshToken

    def parse_user_id(self) -> str:
        """
        Parses the current access token and returns the user ID.
        """
        return self.parse_token()["userId"]

    def parse_token(self) -> dict:
        """
        Parses the current access token and returns the payload as a dictionary.
        """
        return jwt.decode(self._access_token, options={"verify_signature": False})

    def get_access_token(self) -> str:
        """
        Gets the current access token.
        """
        return self._access_token

    def get_refresh_token(self) -> str:
        """
        Gets the current refresh token.
        """
        return self._refresh_token

    def get_user_id(self) -> str:
        """
        Gets the current user ID.
        """
        return self._user_id

    def get_client_id(self) -> str:
        """
        Gets the current client ID.
        """
        return self._client_id
