import os
import logging

from .._client._iam_client import IAMClient
from .._client._video_client import VideoClient
from .._models import *


logger = logging.getLogger(__name__)

class VideoManager:
    """
    A manager for handling video tasks, providing methods to create, update, and stop tasks.
    """

    def __init__(self, iam_client: IAMClient):
        """
        Initializes the VideoManager with the given IAM client.
        """
        self.video_client = VideoClient(iam_client)
        self.iam_client = iam_client

    
    def get_request_detail(self, request_id: str) -> GetRequestResponse:
        """
        Retrieves detailed information about a specific request by its ID. This endpoint requires authentication with a bearer token and only returns requests belonging to the authenticated organization.

        :param request_id: The ID of the request to be retrieved.
        :return: Details of the request successfully retrieved
        """
        self._validate_not_empty(request_id, "request_id")
        return self.video_client.get_request_detail(request_id)


    def get_requests(self, model_id: str) -> List[GetRequestResponse]:
        """
        Retrieves a list of requests submitted by the authenticated user for a specific model. This endpoint requires authentication with a bearer token and filters results by the authenticated organization.

        :param model_id: The ID of the model to be retrieved.
        :return: List of user's requests successfully retrieved
        """
        self._validate_not_empty(model_id, "model_id")
        return self.video_client.get_requests(model_id)


    def create_request(self, request: SubmitRequestRequest) -> SubmitRequestResponse:
        """
        Submits a new asynchronous request to process a specified model with provided parameters. This endpoint requires authentication with a bearer token.

        :param request: The request data to be created.
        :return: The created request data.
        """
        if not request:
            raise ValueError("Request data cannot be None.")
        if not request.model:
            raise ValueError("Model ID is required in the request data.")
        if not request.payload:
            raise ValueError("Payload is required in the request data.")
        return self.video_client.create_request(request)
        
    
    def get_model_detail(self, model_id: str) -> GetModelResponse:
        """
        Retrieves detailed information about a specific model by its ID.

        :param model_id: The ID of the model to be retrieved.
        :return: Details of the specified model.
        """
        self._validate_not_empty(model_id, "model_id")
        return self.video_client.get_model_detail(model_id)


    def get_models(self) -> List[GetModelResponse]:
        """
        Retrieves a list of available models for video processing.

        :return: A list of available models.
        """
        return self.video_client.get_models()


    @staticmethod
    def _validate_not_empty(value: str, name: str):
        """
        Validate a string is neither None nor empty.

        :param value: The string to validate.
        :param name: The name of the value for error reporting.
        """
        if not value or not value.strip():
            raise ValueError(f"{name} is required and cannot be empty.")