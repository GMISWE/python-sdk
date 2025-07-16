import json
import os
from google.oauth2 import id_token
from google.auth.transport import requests
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from .._http_client import HTTPClient
import logging

logger = logging.getLogger(__name__)

class GoogleAuthenticator:
    """Google OAuth2 authentication class"""

    def __init__(self, client: HTTPClient, client_secrets_file=None, scopes=None):
        """
        Initialize Google authenticator
        
        Args:
            client (HTTPClient): HTTP client instance
            client_secrets_file (str): Client secrets file path
            scopes (list): Scope list
        """
        self.client = client
        
        self.scopes = scopes or [
            'openid',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile'
        ]
        self.credentials = None
        self.flow = None
        
        if client_secrets_file:
            if not os.path.exists(client_secrets_file):
                raise FileNotFoundError(f"Client secrets file not found: {client_secrets_file}")
            self.client_secrets_file = client_secrets_file
        else:
            file_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Client secrets file not found: {file_path}")
            self.client_secrets_file = file_path

        if not self.authenticate_manual():
            raise Exception("Authentication failed. Please check your authentication code is correct for the auth url.")

    def authenticate_local_server(self, port=18080, open_browser=True):
        """
        Authenticate using local server
        
        Args:
            port (int): Local server port
            open_browser (bool): Whether to automatically open browser
            
        Returns:
            google.oauth2.credentials.Credentials: Authentication credentials
        """
        try:
            self.flow = InstalledAppFlow.from_client_secrets_file(
                self.client_secrets_file, 
                self.scopes
            )
            
            self.credentials = self.flow.run_local_server(
                port=port, 
                open_browser=open_browser
            )
            
            return self.credentials
            
        except Exception as e:
            print(f"Authentication failed: {e}")
            return None
    
    def authenticate_manual(self):
        """
        Manual authentication method (user needs to manually copy and paste code)
        
        Returns:
            google.oauth2.credentials.Credentials: Authentication credentials
        """
        try:
            # Load client configuration
            with open(self.client_secrets_file, 'r') as f:
                client_config = json.load(f)
            
            # Create flow
            self.flow = InstalledAppFlow.from_client_config(
                client_config, 
                self.scopes,
                redirect_uri='urn:ietf:wg:oauth:2.0:oob'
            )
            
            # Get authorization URL
            auth_url, _ = self.flow.authorization_url(prompt='consent')
            log = f'''
Please visit the following URL to authorize:\n
auth url : \n{auth_url}\n
After authorization, you will get an authorization code, please enter it below:
'''
            print(log)
            
            # Get authorization code
            auth_code = input("Please enter the authorization code: ")
            
            # Exchange code for credentials
            self.flow.fetch_token(code=auth_code)
            
            self.credentials = self.flow.credentials
            
            return self.credentials
            
        except Exception as e:
            print(f"Authentication failed: {e}")
            return None
    
    def get_access_token(self):
        """
        Get access token
        
        Returns:
            str: Access token
        """
        if not self.credentials:
            print("Please authenticate first")
            return None
            
        return self.credentials.token


    def get_user_info(self):
        """
        Get user information
        
        Returns:
            dict: User information dictionary
        """
        if not self.credentials:
            print("Please authenticate first")
            return None
            
        try:
            # Verify ID token and get user information
            idinfo = id_token.verify_oauth2_token(
                self.credentials.id_token,
                requests.Request(),
                audience=self.credentials.client_id
            )
            
            return {
                'email': idinfo.get('email'),
                'name': idinfo.get('name'),
                'picture': idinfo.get('picture'),
                'sub': idinfo.get('sub'),
                'verified_email': idinfo.get('email_verified')
            }
            
        except Exception as e:
            logger.info(f"Failed to get user information: {e}")
            return None


    def gen_user_auth_tokens(self) -> dict:
        """
        Check if user exists in GMICLOUD
        Returns:
            bool: True if user exists, False otherwise
        """
        data = {
            "provider": "google",
            "accessToken": self.get_access_token(),
        }
        try:
            custom_headers = {"CE-ClientId": "gmisdk"}
            authToken = self.client.post(f"/me/oauth/auth-tokens", custom_headers, data=data)
            if not authToken:
                print("Failed to check user existence")
                return None
            logger.info(f"Response from server: {authToken}")
            if authToken.get("code") and authToken.get("code") == 1:
                print(f"Error checking user existence: {authToken.get('message')}, please sign up in GMICLOUD website.")
                return None
            if isinstance(authToken, dict) and 'authToken' in authToken:
                tokens = self.client.post(f"/me/sessions", custom_headers, data=authToken)
                logger.info(f"Auth token: {tokens}")
        except Exception as e:
            raise Exception(f"Error occurred: {e}")
        return tokens