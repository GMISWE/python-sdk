import os
from typing import List
import mimetypes

from typing import Optional

from GMICloud.api.artifacts import ArtifactClient
from GMICloud.http_client.file_upload_client import FileUploadClient
from GMICloud.models import (
    Artifact,
    CreateArtifactRequest,
    CreateArtifactResponse,
    GetBigFileUploadUrlRequest
)


class ArtifactManager:
    """
    Artifact Manager handles creation, retrieval, and file upload associated with artifacts.
    """

    def __init__(self):
        self.artifact_client = ArtifactClient()

    def get_all_artifacts(self, user_id: str) -> List[Artifact]:
        """
        Retrieve all artifacts for a given user.

        :param user_id: The ID of the user whose artifacts should be retrieved.
        :return: A list of Artifact objects associated with the user.
        :raises ValueError: If the `user_id` is None or an empty string.
        """
        self._validate_user_id(user_id)

        return self.artifact_client.get_all_artifacts(user_id)

    def create_artifact(
            self,
            user_id: str,
            artifact_name: str,
            description: Optional[str] = "",
            tags: Optional[str] = ""
    ) -> CreateArtifactResponse:
        """
        Create a new artifact for a user.

        :param user_id: The ID of the user who is creating the artifact.
        :param artifact_name: The name of the artifact.
        :param description: An optional description for the artifact.
        :param tags: Optional tags associated with the artifact, as a comma-separated string.
        :return: A `CreateArtifactResponse` object containing information about the created artifact.
        :raises ValueError: If the `user_id` is None or an empty string.
        """
        self._validate_user_id(user_id)

        req = CreateArtifactRequest(user_id=user_id, artifact_name=artifact_name, artifact_description=description,
                                    artifact_tags=tags, )

        return self.artifact_client.create_artifact(req)

    def create_artifact_with_file(
            self,
            user_id: str,
            artifact_name: str,
            file_path: str,
            description: Optional[str] = "",
            tags: Optional[str] = ""
    ) -> str:
        """
        Create a new artifact for a user and upload a file associated with the artifact.

        :param user_id: The ID of the user who is creating the artifact.
        :param artifact_name: The name of the artifact.
        :param file_path: The local path to the file to be uploaded.
        :param description: An optional description for the artifact.
        :param tags: Optional tags associated with the artifact, as a comma-separated string.
        :return: The `artifact_id` of the created artifact.
        :raises ValueError: If the `user_id` or `file_path` is None or empty.
        :raises FileNotFoundError: If the provided `file_path` does not exist.
        """
        self._validate_user_id(user_id)
        self._validate_file_path(file_path)

        # Extract file details
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)
        file_type = mimetypes.guess_type(file_path)[0]

        # Create the artifact
        create_artifact_resp = self.create_artifact(user_id, artifact_name, description, tags)
        artifact_id = create_artifact_resp.artifact_id

        # Handle file upload
        if file_size <= 5 * 1024 * 1024 * 1024:  # Small file: <= 5GB
            FileUploadClient.upload_small_file(create_artifact_resp.upload_link, file_path, file_type)
        else:
            bigfile_upload_url_resp = self.artifact_client.get_bigfile_upload_url(
                GetBigFileUploadUrlRequest(artifact_id=artifact_id, file_name=file_name, file_type=file_type)
            )
            FileUploadClient.upload_large_file(bigfile_upload_url_resp.upload_link, file_path)

        return artifact_id

    @staticmethod
    def _validate_user_id(user_id: str) -> None:
        """
        Validate the user ID.

        :param user_id: The user ID to validate.
        :raises ValueError: If `user_id` is None or empty.
        """
        if not user_id or not user_id.strip():
            raise ValueError("User ID is required and cannot be empty.")

    @staticmethod
    def _validate_file_path(file_path: str) -> None:
        """
        Validate the file path.

        :param file_path: The file path to validate.
        :raises ValueError: If `file_path` is None or empty.
        :raises FileNotFoundError: If the provided `file_path` does not exist.
        """
        if not file_path or not file_path.strip():
            raise ValueError("File path is required and cannot be empty.")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")


if __name__ == '__main__':
    try:
        artifact_manager = ArtifactManager()
        # artifact_manager.create_artifact_with_file("user_id", "artifact_name", "/Users/57block/Downloads/filtered_report.png", "description", "tags")
        print(artifact_manager.get_all_artifacts("904c002c-8327-4bd4-8e73-0dcd04775f63"))
    except Exception as e:
        print(e)
