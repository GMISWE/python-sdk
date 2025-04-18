import jwt
import logging
from requests.exceptions import RequestException

from ._http_client import HTTPClient
from .._config import IAM_SERVICE_BASE_URL
from .._models import *
from .._constants import CLIENT_ID_HEADER, AUTHORIZATION_HEADER

logger = logging.getLogger(__name__)


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
        self._organization_id = ""
        self.client = HTTPClient(IAM_SERVICE_BASE_URL)

    def login(self) -> bool:
        """
        Logs in a user with the given email and password.
        Returns True if login is successful, otherwise False.
        """
        try:
            custom_headers = {CLIENT_ID_HEADER: self._client_id}
            req = AuthTokenRequest(email=self._email, password=self._password)
            auth_tokens_result = self.client.post("/me/auth-tokens", custom_headers, req.model_dump())

            if not auth_tokens_result:
                logger.error("Login failed: Received empty response from auth-tokens endpoint")
                return False

            auth_tokens_resp = AuthTokenResponse.model_validate(auth_tokens_result)

            # Handle 2FA
            if auth_tokens_resp.is2FARequired:
                for attempt in range(3):
                    code = input(f"Attempt {attempt + 1}/3: Please enter the 2FA code: ")
                    create_session_req = CreateSessionRequest(
                        type="native", authToken=auth_tokens_resp.authToken, otpCode=code
                    )
                    try:
                        session_result = self.client.post("/me/sessions", custom_headers,
                                                          create_session_req.model_dump())
                        if session_result:
                            break
                    except RequestException:
                        logger.warning("Invalid 2FA code, please try again.")
                        if attempt == 2:
                            logger.error("Failed to create session after 3 incorrect 2FA attempts.")
                            return False
            else:
                create_session_req = CreateSessionRequest(type="native", authToken=auth_tokens_resp.authToken,
                                                          otpCode=None)
                session_result = self.client.post("/me/sessions", custom_headers, create_session_req.model_dump())

            create_session_resp = CreateSessionResponse.model_validate(session_result)

            self._access_token = create_session_resp.accessToken
            self._refresh_token = create_session_resp.refreshToken
            self._user_id = self.parse_user_id()

            # Fetch profile to get organization ID
            profile_result = self.client.get("/me/profile", self.get_custom_headers())
            if not profile_result:
                logger.error("Failed to fetch user profile data.")
                return False

            profile_resp = ProfileResponse.model_validate(profile_result)
            self._organization_id = profile_resp.organization.id

            return True
        except (RequestException, ValueError, KeyError) as e:
            logger.error(f"Login failed due to exception: {e}")
            return False

    def refresh_token(self) -> bool:
        """
        Refreshes the access token. Returns True on success, False otherwise.
        """
        try:
            custom_headers = {CLIENT_ID_HEADER: self._client_id}
            result = self.client.patch("/me/sessions", custom_headers, {"refreshToken": self._refresh_token})

            if not result:
                logger.error("Failed to refresh token: Empty response received")
                return False

            resp = CreateSessionResponse.model_validate(result)
            self._access_token = resp.accessToken
            self._refresh_token = resp.refreshToken

            return True
        except (RequestException, ValueError) as e:
            logger.error(f"Token refresh failed: {e}")
            return False

    def create_org_api_key(self, request: CreateAPIKeyRequest) -> Optional[str]:
        """
        Creates a new API key for the current user.
        """
        try:
            result = self.client.post(f"/organizations/{self.get_organization_id()}/api-keys",
                                      self.get_custom_headers(), request.model_dump())

            return CreateAPIKeyResponse.model_validate(result).key if result else None
        except (RequestException, ValueError) as e:
            logger.error(f"Failed to create API key: {e}")
            return None

    def get_org_api_keys(self) -> Optional[GetAPIKeysResponse]:
        """
        Fetches all API keys for the current user.
        """
        try:
            result = self.client.get(f"/organizations/{self.get_organization_id()}/api-keys",
                                     self.get_custom_headers())

            return GetAPIKeysResponse.model_validate(result) if result else None
        except (RequestException, ValueError) as e:
            logger.error(f"Failed to retrieve organization API keys: {e}")
            return None

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

    def get_organization_id(self) -> str:
        """
        Gets the current organization ID.
        """
        return self._organization_id

    def get_custom_headers(self) -> dict:
        """
        Gets the custom headers for the IAM client.
        """
        return {
            AUTHORIZATION_HEADER: f'Bearer {self._access_token}',
            CLIENT_ID_HEADER: self._client_id
        }
