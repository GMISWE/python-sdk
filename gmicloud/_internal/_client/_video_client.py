
import logging
from requests.exceptions import RequestException

from ._http_client import HTTPClient
from ._decorator import handle_refresh_token
from ._iam_client import IAMClient
from .._config import IAM_SERVICE_BASE_URL
from .._models import *


logger = logging.getLogger(__name__)


class VideoClient:
    """
    A client for interacting with the video service API.

    This client provides methods to retrieve, create, update, and stop video tasks
    through HTTP calls to the video service.
    """

    def __init__(self, iam_client: IAMClient):
        """
        Initializes the VideoClient with the given base URL for the video service.
        """
        self.client = HTTPClient(IAM_SERVICE_BASE_URL+ "/ie/requestqueue")
        self.iam_client = iam_client


    @handle_refresh_token
    def get_request_detail(self, request_id: str) -> GetRequestResponse:
        """
        Retrieves detailed information about a specific request by its ID. This endpoint requires authentication with a bearer token and only returns requests belonging to the authenticated organization.

        :param request_id: The ID of the request to be retrieved.
        :return: Details of the GetRequestResponse successfully retrieved
        """
        try:
            response = self.client.get(f"/requests/{request_id}", self.iam_client.get_custom_headers())
            return GetRequestResponse.model_validate(response) if response else None
        except (RequestException, ValueError) as e:
            logger.error(f"Failed to retrieve request details for {request_id}: {e}")
            return None


    @handle_refresh_token
    def get_requests(self, model_id: str) -> List[GetRequestResponse]:
        """
        Retrieves a list of requests submitted by the authenticated user for a specific model. This endpoint requires authentication with a bearer token and filters results by the authenticated organization.

        :param model_id: The ID of the model to be retrieved.
        :return: List of GetRequestResponse successfully retrieved
        """
        try:
            response = self.client.get("/requests", self.iam_client.get_custom_headers(), {"model_id": model_id})
            requests = response.get('requests', []) if response else []
            return [GetRequestResponse.model_validate(req) for req in requests] if requests else None
        except (RequestException, ValueError) as e:
            logger.error(f"Failed to retrieve requests for model {model_id}: {e}")
            return None


    @handle_refresh_token
    def create_request(self, request: SubmitRequestRequest) -> SubmitRequestResponse:
        """
        Submits a new asynchronous request to process a specified model with provided parameters. This endpoint requires authentication with a bearer token.

        :param request: The request data to be created by SubmitRequestRequest model.
        :return: The created request data as SubmitRequestResponse model.
        """
        try:
            response = self.client.post("/requests", self.iam_client.get_custom_headers(), request.model_dump())
            return SubmitRequestResponse.model_validate(response) if response else None
        except (RequestException, ValueError) as e:
            logger.error(f"Failed to create request: {e}")
            return None


    @handle_refresh_token
    def get_model_detail(self, model_id: str) -> GetModelResponse:
        """
        Retrieves detailed information about a specific model by its ID.

        :param model_id: The ID of the model to be retrieved.
        :return: Details of the GetModelResponse model successfully retrieved.
        """
        try:
            response = self.client.get(f"/models/{model_id}", self.iam_client.get_custom_headers())
            return GetModelResponse.model_validate(response) if response else None
        except (RequestException, ValueError) as e:
            logger.error(f"Failed to retrieve model details for {model_id}: {e}")
            return None    
    

    @handle_refresh_token
    def get_models(self) -> List[GetModelResponse]:
        """
        Retrieves a list of available models from the video service.

        :return: A list of GetModelResponse model successfully retrieved.
        """
        try:
            response = self.client.get("/models", self.iam_client.get_custom_headers())
            models = response.get('models', []) if response else []
            return [GetModelResponse.model_validate(model) for model in models] if models else None
        except (RequestException, ValueError) as e:
            logger.error(f"Failed to retrieve models: {e}")
            return None
    

