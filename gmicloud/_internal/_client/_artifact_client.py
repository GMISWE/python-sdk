from typing import List
import logging
from requests.exceptions import RequestException

from ._http_client import HTTPClient
from ._iam_client import IAMClient
from ._decorator import handle_refresh_token
from .._models import *
from .._config import ARTIFACT_SERVICE_BASE_URL

logger = logging.getLogger(__name__)


class ArtifactClient:
    """
    Client for interacting with the Artifact Service API.

    This client provides methods to perform CRUD operations on artifacts,
    as well as generating signed URLs for uploading large files.
    """

    def __init__(self, iam_client: IAMClient):
        """
        Initializes the ArtifactClient with an HTTPClient configured
        to communicate with the Artifact Service base URL.
        """
        self.client = HTTPClient(ARTIFACT_SERVICE_BASE_URL)
        self.iam_client = iam_client

    @handle_refresh_token
    def get_artifact(self, artifact_id: str) -> Optional[Artifact]:
        """
        Fetches an artifact by its ID.

        :param artifact_id: The ID of the artifact to fetch.
        :return: The Artifact object or None if an error occurs.
        """
        try:
            response = self.client.get(
                "/get_artifact",
                self.iam_client.get_custom_headers(),
                {"artifact_id": artifact_id}
            )
            return Artifact.model_validate(response) if response else None
        except (RequestException, ValueError) as e:
            logger.error(f"Failed to fetch artifact {artifact_id}: {e}")
            return None

    @handle_refresh_token
    def get_all_artifacts(self) -> List[Artifact]:
        """
        Fetches all artifacts.

        :return: A list of Artifact objects. If an error occurs, returns an empty list.
        """
        try:
            response = self.client.get("/get_all_artifacts", self.iam_client.get_custom_headers())
            if not response:
                logger.error("Empty response from /get_all_artifacts")
                return []
            return [Artifact.model_validate(item) for item in response]
        except (RequestException, ValueError) as e:
            logger.error(f"Failed to fetch all artifacts: {e}")
            return []

    @handle_refresh_token
    def create_artifact(self, request: CreateArtifactRequest) -> Optional[CreateArtifactResponse]:
        """
        Creates a new artifact in the service.

        :param request: The request object containing artifact details.
        :return: The response object containing the created artifact details, or None on error.
        """
        try:
            response = self.client.post(
                "/create_artifact",
                self.iam_client.get_custom_headers(),
                request.model_dump()
            )
            return CreateArtifactResponse.model_validate(response) if response else None
        except (RequestException, ValueError) as e:
            logger.error(f"Failed to create artifact: {e}")
            return None

    @handle_refresh_token
    def create_artifact_from_template(self, artifact_template_id: str) -> Optional[CreateArtifactFromTemplateResponse]:
        """
        Creates a new artifact in the service.

        :param artifact_template_id: The ID of the artifact template to use.
        :return: The response object containing the created artifact details or None if an error occurs.
        """
        try:
            response = self.client.post(
                "/create_artifact_from_template",
                self.iam_client.get_custom_headers(),
                {"artifact_template_id": artifact_template_id}
            )
            return CreateArtifactFromTemplateResponse.model_validate(response) if response else None
        except (RequestException, ValueError) as e:
            logger.error(f"Failed to create artifact from template {artifact_template_id}: {e}")
            return None

    @handle_refresh_token
    def rebuild_artifact(self, artifact_id: str) -> Optional[RebuildArtifactResponse]:
        """
        Rebuilds an artifact in the service.

        :param artifact_id: The ID of the artifact to rebuild.
        :return: The response object containing the rebuilt artifact details or None if an error occurs.
        """
        try:
            response = self.client.post(
                "/rebuild_artifact",
                self.iam_client.get_custom_headers(),
                {"artifact_id": artifact_id}
            )
            return RebuildArtifactResponse.model_validate(response) if response else None
        except (RequestException, ValueError) as e:
            logger.error(f"Failed to rebuild artifact {artifact_id}: {e}")
            return None

    @handle_refresh_token
    def delete_artifact(self, artifact_id: str) -> Optional[DeleteArtifactResponse]:
        """
        Deletes an artifact by its ID.

        :param artifact_id: The ID of the artifact to delete.
        :return: The response object containing the deleted artifact details or None if an error occurs.
        """
        try:
            response = self.client.delete(
                "/delete_artifact",
                self.iam_client.get_custom_headers(),
                {"artifact_id": artifact_id}
            )
            return DeleteArtifactResponse.model_validate(response) if response else None
        except (RequestException, ValueError) as e:
            logger.error(f"Failed to delete artifact {artifact_id}: {e}")
            return None

    @handle_refresh_token
    def get_bigfile_upload_url(self, request: GetBigFileUploadUrlRequest) -> Optional[GetBigFileUploadUrlResponse]:
        """
        Generates a pre-signed URL for uploading a large file.

        :param request: The request object containing the artifact ID, file name, and file type.
        :return: The response object containing the pre-signed URL and upload details, or None if an error occurs.
        """
        try:
            response = self.client.post("/get_bigfile_upload_url",
                                        self.iam_client.get_custom_headers(),
                                        request.model_dump())

            if not response:
                logger.error("Empty response from /get_bigfile_upload_url")
                return None

            return GetBigFileUploadUrlResponse.model_validate(response)

        except (RequestException, ValueError) as e:
            logger.error(f"Failed to generate upload URL: {e}")
            return None

    @handle_refresh_token
    def delete_bigfile(self, request: DeleteBigfileRequest) -> Optional[DeleteBigfileResponse]:
        """
        Deletes a large file associated with an artifact.

        :param request: The request object containing the artifact ID and file name.
        :return: The response object containing the deletion status, or None if an error occurs.
        """
        try:
            response = self.client.delete("/delete_bigfile",
                                          self.iam_client.get_custom_headers(),
                                          request.model_dump())

            if not response:
                logger.error("Empty response from /delete_bigfile")
                return None

            return DeleteBigfileResponse.model_validate(response)

        except (RequestException, ValueError) as e:
            logger.error(f"Failed to delete big file: {e}")
            return None

    @handle_refresh_token
    def get_public_templates(self) -> List[ArtifactTemplate]:
        """
        Fetches all artifact templates.

        :return: A list of ArtifactTemplate objects.
        :rtype: List[ArtifactTemplate]
        """
        try:
            response = self.client.get("/get_public_templates", self.iam_client.get_custom_headers())

            if not response:
                logger.error("Empty response received from /get_public_templates API")
                return []

            try:
                result = GetPublicTemplatesResponse.model_validate(response)
                return result.artifact_templates
            except ValueError as ve:
                logger.error(f"Failed to validate response data: {ve}")
                return []

        except RequestException as e:
            logger.error(f"Request to /get_public_templates failed: {e}")
            return []
