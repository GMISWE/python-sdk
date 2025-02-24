import os
from typing import List
import mimetypes

from .._client._iam_client import IAMClient
from .._client._artifact_client import ArtifactClient
from .._client._file_upload_client import FileUploadClient
from .._models import *


class ArtifactManager:
    """
    Artifact Manager handles creation, retrieval, and file upload associated with artifacts.
    """

    def __init__(self, iam_client: IAMClient):
        """
        Initialize the ArtifactManager instance with the user ID and access token.

        :param iam_client: The IAMClient instance to use for authentication.
        :raises ValueError: If the `user_id` is None or an empty string.
        """
        self.iam_client = iam_client
        self.artifact_client = ArtifactClient(iam_client)

    def get_artifact(self, artifact_id: str) -> Artifact:
        """
        Retrieve an artifact by its ID.

        :param artifact_id: The ID of the artifact to retrieve.
        :return: The Artifact object associated with the ID.
        :rtype: Artifact
        :raises ValueError: If `artifact_id` is None or empty.
        """
        self._validate_artifact_id(artifact_id)

        return self.artifact_client.get_artifact(artifact_id)

    def get_all_artifacts(self) -> List[Artifact]:
        """
        Retrieve all artifacts for a given user.

        :return: A list of Artifact objects associated with the user.
        :rtype: List[Artifact]
        """
        return self.artifact_client.get_all_artifacts()

    def create_artifact(
            self,
            artifact_name: str,
            description: Optional[str] = "",
            tags: Optional[List[str]] = None
    ) -> CreateArtifactResponse:
        """
        Create a new artifact for a user.

        :param artifact_name: The name of the artifact.
        :param description: An optional description for the artifact.
        :param tags: Optional tags associated with the artifact, as a comma-separated string.
        :return: A `CreateArtifactResponse` object containing information about the created artifact.
        :rtype: CreateArtifactResponse
        """
        if not artifact_name or not artifact_name.strip():
            raise ValueError("Artifact name is required and cannot be empty.")

        req = CreateArtifactRequest(artifact_name=artifact_name,
                                    artifact_description=description,
                                    artifact_tags=tags, )

        return self.artifact_client.create_artifact(req)

    def create_artifact_from_template(self, artifact_template_id: str) -> str:
        """
        Create a new artifact for a user using a template.

        :param artifact_template_id: The ID of the template to use for the artifact.
        :return: The `artifact_id` of the created artifact.
        :rtype: str
        :raises ValueError: If `artifact_template_id` is None or empty.
        """
        if not artifact_template_id or not artifact_template_id.strip():
            raise ValueError("Artifact template ID is required and cannot be empty.")

        resp = self.artifact_client.create_artifact_from_template(artifact_template_id)
        if not resp or not resp.artifact_id:
            raise ValueError("Failed to create artifact from template.")

        return resp.artifact_id

    def rebuild_artifact(self, artifact_id: str) -> RebuildArtifactResponse:
        """
        Rebuild an existing artifact.

        :param artifact_id: The ID of the artifact to rebuild.
        :return: A `RebuildArtifactResponse` object containing information about the rebuilt artifact.
        :rtype: RebuildArtifactResponse
        :raises ValueError: If `artifact_id` is None or empty
        """
        self._validate_artifact_id(artifact_id)

        return self.artifact_client.rebuild_artifact(artifact_id)

    def delete_artifact(self, artifact_id: str) -> DeleteArtifactResponse:
        """
        Delete an existing artifact.

        :param artifact_id: The ID of the artifact to delete.
        :return: A `DeleteArtifactResponse` object containing information about the deleted artifact.
        :rtype: DeleteArtifactResponse
        :raises ValueError: If `artifact_id` is None or empty
        """
        self._validate_artifact_id(artifact_id)

        return self.artifact_client.delete_artifact(artifact_id)

    def upload_artifact_file(self, upload_link: str, artifact_file_path: str) -> None:
        """
        Upload a file associated with an artifact.

        :param upload_link: The URL to upload the artifact file.
        :param artifact_file_path: The path to the artifact file.
        :raises ValueError: If `file_path` is None or empty.
        :raises FileNotFoundError: If the provided `file_path` does not exist.
        """
        self._validate_artifact_file_path(artifact_file_path)
        artifact_file_type = mimetypes.guess_type(artifact_file_path)[0]

        FileUploadClient.upload_small_file(upload_link, artifact_file_path, artifact_file_type)

    def create_artifact_with_file(
            self,
            artifact_name: str,
            artifact_file_path: str,
            description: Optional[str] = "",
            tags: Optional[List[str]] = None
    ) -> str:
        """
        Create a new artifact for a user and upload a file associated with the artifact.

        :param artifact_name: The name of the artifact.
        :param artifact_file_path: The path to the artifact file(Dockerfile+serve.py).
        :param description: An optional description for the artifact.
        :param tags: Optional tags associated with the artifact, as a comma-separated string.
        :return: The `artifact_id` of the created artifact.
        :rtype: str
        :raises FileNotFoundError: If the provided `file_path` does not exist.
        """
        self._validate_artifact_file_path(artifact_file_path)

        # Create the artifact
        create_artifact_resp = self.create_artifact(artifact_name, description, tags)
        artifact_id = create_artifact_resp.artifact_id

        artifact_file_type = mimetypes.guess_type(artifact_file_path)[0]
        FileUploadClient.upload_small_file(create_artifact_resp.upload_link, artifact_file_path, artifact_file_type)

        return artifact_id

    def get_bigfile_upload_url(self, artifact_id: str, model_file_path: str) -> str:
        """
        Generate a pre-signed URL for uploading a large file associated with an artifact.

        :param artifact_id: The ID of the artifact for which the file is being uploaded.
        :param model_file_path: The path to the model file.
        :return: The pre-signed upload URL for the large file.
        :rtype: str
        :raises ValueError: If `artifact_id` is None or empty.
        """
        self._validate_artifact_id(artifact_id)
        self._validate_file_path(model_file_path)

        model_file_name = os.path.basename(model_file_path)
        model_file_type = mimetypes.guess_type(model_file_path)[0]

        req = GetBigFileUploadUrlRequest(artifact_id=artifact_id, file_name=model_file_name, file_type=model_file_type)

        resp = self.artifact_client.get_bigfile_upload_url(req)
        if not resp or not resp.upload_link:
            raise ValueError("Failed to get bigfile upload URL.")

        return resp.upload_link

    def delete_bigfile(self, artifact_id: str, file_name: str) -> str:
        """
        Delete a large file associated with an artifact.

        :param artifact_id: The ID of the artifact for which the file is being deleted.
        :param file_name: The name of the file being deleted.
        """
        self._validate_artifact_id(artifact_id)
        self._validate_file_name(file_name)

        resp = self.artifact_client.delete_bigfile(artifact_id, file_name)
        if not resp or not resp.status:
            raise ValueError("Failed to delete bigfile.")

        return resp.status

    def upload_large_file(self, upload_link: str, file_path: str) -> None:
        """
        Upload a large file to the specified URL.

        :param upload_link: The URL to upload the file.
        :param file_path: The path to the file to upload.
        :raises ValueError: If `file_path` is None or empty.
        :raises ValueError: If `upload_link` is None or empty.
        :raises FileNotFoundError: If the provided `file_path` does not exist.
        """
        self._validate_file_path(file_path)
        self._validate_upload_url(upload_link)

        FileUploadClient.upload_large_file(upload_link, file_path)

    def create_artifact_with_model_files(
            self,
            artifact_name: str,
            artifact_file_path: str,
            model_file_paths: List[str],
            description: Optional[str] = "",
            tags: Optional[str] = None
    ) -> str:
        """
        Create a new artifact for a user and upload model files associated with the artifact.

        :param artifact_name: The name of the artifact.
        :param artifact_file_path: The path to the artifact file(Dockerfile+serve.py).
        :param model_file_paths: The paths to the model files.
        :param description: An optional description for the artifact.
        :param tags: Optional tags associated with the artifact, as a comma-separated string.
        :return: The `artifact_id` of the created artifact.
        :raises FileNotFoundError: If the provided `file_path` does not exist.
        """
        artifact_id = self.create_artifact_with_file(artifact_name, artifact_file_path, description, tags)

        for model_file_path in model_file_paths:
            self._validate_file_path(model_file_path)
            bigfile_upload_url_resp = self.artifact_client.get_bigfile_upload_url(
                GetBigFileUploadUrlRequest(artifact_id=artifact_id, model_file_path=model_file_path)
            )
            FileUploadClient.upload_large_file(bigfile_upload_url_resp.upload_link, model_file_path)

        return artifact_id

    def get_public_templates(self) -> List[ArtifactTemplate]:
        """
        Fetch all artifact templates.

        :return: A list of ArtifactTemplate objects.
        :rtype: List[ArtifactTemplate]
        """
        return self.artifact_client.get_public_templates()

    @staticmethod
    def _validate_file_name(file_name: str) -> None:
        """
        Validate the file name.

        :param file_name: The file name to validate.
        :raises ValueError: If `file_name` is None or empty.
        """
        if not file_name or not file_name.strip():
            raise ValueError("File name is required and cannot be empty.")

    @staticmethod
    def _validate_artifact_id(artifact_id: str) -> None:
        """
        Validate the artifact ID.

        :param artifact_id: The artifact ID to validate.
        :raises ValueError: If `artifact_id` is None or empty.
        """
        if not artifact_id or not artifact_id.strip():
            raise ValueError("Artifact ID is required and cannot be empty.")

    @staticmethod
    def _validate_artifact_file_path(artifact_file_path: str) -> None:
        """
        Validate the artifact file path.

        :param artifact_file_path: The file path to validate.
        :raises ValueError: If `file_path` is None or empty.
        :raises FileNotFoundError: If the provided `file_path` does not exist.
        """
        ArtifactManager._validate_file_path(artifact_file_path)

        file_type = mimetypes.guess_type(artifact_file_path)[0]
        if file_type != "application/zip":
            raise ValueError("File type must be application/zip.")

    @staticmethod
    def _validate_upload_url(upload_link: str) -> None:
        """
        Validate the upload URL.

        :param upload_link: The upload URL to validate.
        :raises ValueError: If `upload_link` is None or empty.
        """
        if not upload_link or not upload_link.strip():
            raise ValueError("Upload link is required and cannot be empty.")

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
