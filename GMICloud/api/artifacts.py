from typing import List

from GMICloud.http_client.http_client import HTTPClient
from GMICloud.models import *
from GMICloud.config import ARTIFACT_SERVICE_BASE_URL


class ArtifactClient:
    """
    Client for interacting with the Artifact Service API.

    This client provides methods to perform CRUD operations on artifacts,
    as well as generating signed URLs for uploading large files.
    """

    def __init__(self):
        """
        Initializes the ArtifactClient with an HTTPClient configured
        to communicate with the Artifact Service base URL.
        """
        self.client = HTTPClient(ARTIFACT_SERVICE_BASE_URL)

    def get_all_artifacts(self, user_id: str) -> List[Artifact]:
        """
        Fetches all artifacts for a given user ID.

        :param user_id: The ID of the user whose artifacts are being fetched.
        :return: A list of Artifact objects.
        :rtype: List[Artifact]
        """
        result = self.client.post("/artifact-api/v1/get_all_artifacts", "", {"user_id": user_id})

        return [Artifact.model_validate(item) for item in result]

    def create_artifact(self, request: CreateArtifactRequest) -> CreateArtifactResponse:
        """
        Creates a new artifact in the service.

        :param request: The request object containing artifact details.
        :return: The response object containing the created artifact details.
        :rtype: CreateArtifactResponse
        """
        result = self.client.post("/artifact-api/v1/create_artifact", "", request.model_dump())

        return CreateArtifactResponse.model_validate(result)

    def get_bigfile_upload_url(self, request: GetBigFileUploadUrlRequest) -> GetBigFileUploadUrlResponse:
        """
        Generates a pre-signed URL for uploading a large file.

        :param request: The request object containing the artifact ID, file name, and file type.
        :return: The response object containing the pre-signed URL and upload details.
        :rtype: GetBigFileUploadUrlResponse
        """
        result = self.client.post("/artifact-api/v1/get_bigfile_upload_url", "", request.model_dump())

        return GetBigFileUploadUrlResponse.model_validate(result)


if __name__ == '__main__':
    try:
        reqeust = GetBigFileUploadUrlRequest(artifact_id="ad035d95-202c-4a2e-b1be-7722b3dd9fb8", file_name="test.zip",
                                             file_type="application/zip")
        resp = ArtifactClient().get_bigfile_upload_url(reqeust)
        print(resp)
    except Exception as e:
        print(e)
