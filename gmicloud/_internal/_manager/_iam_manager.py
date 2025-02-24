from datetime import datetime
from .._client._iam_client import IAMClient
from .._models import *


class IAMManager:
    """
    IamManager handles operations related to IAM, including user authentication and authorization.
    """

    def __init__(self, iam_client: IAMClient):
        """
        Initialize the IAMManager instance and the associated IAMClient.
        """
        self.iam_client = iam_client

    def create_org_api_key(self, name: str, expires_at: Optional[int] = None) -> str:
        """
        Creates a new API key for the current user.
        """

        if not name:
            raise ValueError("API key name cannot be empty")
        if not expires_at:
            # Set the expiration date to 30 days from now
            expires_at = int(datetime.now().timestamp()) + 30 * 24 * 60 * 60
            print(expires_at)

        return self.iam_client.create_org_api_key(
            CreateAPIKeyRequest(name=name, type="ie_model", expiresAt=expires_at))

    def get_org_api_keys(self) -> List[APIKey]:
        """
        Fetches all API keys for the current user.
        """
        return self.iam_client.get_org_api_keys().keys
