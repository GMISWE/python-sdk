from typing import List

from ._http_client import HTTPClient
from ._iam_client import IAMClient
from ._decorator import handle_refresh_token
from .._models import *
from .._config import ARTIFACT_SERVICE_BASE_URL
from .._constants import ACCESS_TOKEN_HEADER, CLIENT_ID_HEADER


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
    def get_artifact(self, artifact_id: str) -> Artifact:
        """
        Fetches an artifact by its ID.

        :param artifact_id: The ID of the artifact to fetch.
        :return: The Artifact object.
        :rtype: Artifact
        """
        custom_headers = {
            ACCESS_TOKEN_HEADER: self.iam_client.get_access_token(),
            CLIENT_ID_HEADER: self.iam_client.get_client_id()
        }
        result = self.client.get(f"/get_artifact", custom_headers, {"artifact_id": artifact_id})

        return Artifact.model_validate(result)

    @handle_refresh_token
    def get_all_artifacts(self) -> List[Artifact]:
        """
        Fetches all artifacts.

        :return: A list of Artifact objects.
        :rtype: List[Artifact]
        """
        custom_headers = {
            ACCESS_TOKEN_HEADER: self.iam_client.get_access_token(),
            CLIENT_ID_HEADER: self.iam_client.get_client_id()
        }
        result = self.client.get("/get_all_artifacts", custom_headers)
        if not result:
            return []
        return [Artifact.model_validate(item) for item in result]

    @handle_refresh_token
    def create_artifact(self, request: CreateArtifactRequest) -> CreateArtifactResponse:
        """
        Creates a new artifact in the service.

        :param request: The request object containing artifact details.
        :return: The response object containing the created artifact details.
        :rtype: CreateArtifactResponse
        """
        custom_headers = {
            ACCESS_TOKEN_HEADER: self.iam_client.get_access_token(),
            CLIENT_ID_HEADER: self.iam_client.get_client_id()
        }
        result = self.client.post("/create_artifact", custom_headers, request.model_dump())

        return CreateArtifactResponse.model_validate(result)

    @handle_refresh_token
    def create_artifact_from_template(self, artifact_template_id: str) -> CreateArtifactFromTemplateResponse:
        """
        Creates a new artifact in the service.

        :param artifact_template_id: The ID of the artifact template to use.
        :return: The response object containing the created artifact details.
        :rtype: CreateArtifactFromTemplateResponse
        """
        custom_headers = {
            ACCESS_TOKEN_HEADER: self.iam_client.get_access_token(),
            CLIENT_ID_HEADER: self.iam_client.get_client_id()
        }
        result = self.client.post("/create_artifact_from_template", custom_headers,
                                  {"artifact_template_id": artifact_template_id})

        return CreateArtifactFromTemplateResponse.model_validate(result)

    @handle_refresh_token
    def rebuild_artifact(self, artifact_id: str) -> RebuildArtifactResponse:
        """
        Rebuilds an artifact in the service.

        :param artifact_id: The ID of the artifact to rebuild.
        :return: The response object containing the rebuilt artifact details.
        :rtype: RebuildArtifactResponse
        """
        custom_headers = {
            ACCESS_TOKEN_HEADER: self.iam_client.get_access_token(),
            CLIENT_ID_HEADER: self.iam_client.get_client_id()
        }
        result = self.client.post("/rebuild_artifact", custom_headers, {"artifact_id": artifact_id})

        return CreateArtifactResponse.model_validate(result)

    @handle_refresh_token
    def delete_artifact(self, artifact_id: str) -> DeleteArtifactResponse:
        """
        Deletes an artifact by its ID.

        :param artifact_id: The ID of the artifact to delete.
        :return: The response object containing the deleted artifact details.
        :rtype: DeleteArtifactResponse
        """
        custom_headers = {
            ACCESS_TOKEN_HEADER: self.iam_client.get_access_token(),
            CLIENT_ID_HEADER: self.iam_client.get_client_id()
        }
        result = self.client.delete("/delete_artifact", custom_headers, {"artifact_id": artifact_id})

        return DeleteArtifactResponse.model_validate(result)

    @handle_refresh_token
    def get_bigfile_upload_url(self, request: GetBigFileUploadUrlRequest) -> GetBigFileUploadUrlResponse:
        """
        Generates a pre-signed URL for uploading a large file.

        :param request: The request object containing the artifact ID, file name, and file type.
        :return: The response object containing the pre-signed URL and upload details.
        :rtype: GetBigFileUploadUrlResponse
        """
        custom_headers = {
            ACCESS_TOKEN_HEADER: self.iam_client.get_access_token(),
            CLIENT_ID_HEADER: self.iam_client.get_client_id()
        }
        result = self.client.post("/get_bigfile_upload_url", custom_headers, request.model_dump())

        return GetBigFileUploadUrlResponse.model_validate(result)

    @handle_refresh_token
    def delete_bigfile(self, request: DeleteBigfileRequest) -> DeleteBigfileResponse:
        """
        Deletes a large file associated with an artifact.

        :param request: The request object containing the artifact ID and file name.
        :return: The response object containing the deletion status.
        :rtype: DeleteBigfileResponse
        """
        custom_headers = {
            ACCESS_TOKEN_HEADER: self.iam_client.get_access_token(),
            CLIENT_ID_HEADER: self.iam_client.get_client_id()
        }
        result = self.client.delete("/delete_bigfile", custom_headers, request.dict())

        return DeleteBigfileResponse.model_validate(result)

    @handle_refresh_token
    def get_artifact_templates(self) -> GetArtifactTemplatesResponse:
        """
        Fetches all artifact templates.

        :return: A list of ArtifactTemplate objects.
        :rtype: List[ArtifactTemplate]
        """
        custom_headers = {
            ACCESS_TOKEN_HEADER: self.iam_client.get_access_token(),
            CLIENT_ID_HEADER: self.iam_client.get_client_id()
        }
        result = self.client.get("/get_artifact_templates", custom_headers)
        return GetArtifactTemplatesResponse.model_validate(result)
