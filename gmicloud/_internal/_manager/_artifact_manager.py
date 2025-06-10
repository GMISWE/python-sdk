import os
import time
from typing import List, Dict, Any
import mimetypes
import concurrent.futures
import re
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from .._client._iam_client import IAMClient
from .._client._artifact_client import ArtifactClient
from .._client._file_upload_client import FileUploadClient
from .._models import *
from .._manager.serve_command_utils import parse_server_command, extract_gpu_num_from_serve_command

import logging

logger = logging.getLogger(__name__)

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
            tags: Optional[List[str]] = None,
            deployment_type: Optional[str] = "",
            template_id: Optional[str] = "",
            env_parameters: Optional[List["EnvParameter"]] = None,
            model_description: Optional[str] = "",
            model_parameters: Optional[List["ModelParameter"]] = None,
            artifact_volume_path: Optional[str] = "",
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
                                    artifact_tags=tags,
                                    deployment_type=deployment_type,
                                    template_id=template_id,
                                    env_parameters=env_parameters,
                                    model_description=model_description,
                                    model_parameters=model_parameters,
                                    artifact_volume_path=artifact_volume_path)

        return self.artifact_client.create_artifact(req)

    def create_artifact_from_template(self, artifact_template_id: str, env_parameters: Optional[dict[str, str]] = None) -> str:
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

        if env_parameters:
            self.artifact_client.add_env_parameters_to_artifact(resp.artifact_id, env_parameters)

        return resp.artifact_id

    
    def create_artifact_from_template_name(self, artifact_template_name: str) -> tuple[str, ReplicaResource]:
        """
        Create an artifact from a template.
        :param artifact_template_name: The name of the template to use.
        :return: A tuple containing the artifact ID and the recommended replica resources.
        :rtype: tuple[str, ReplicaResource]
        """

        recommended_replica_resources = None
        template_id = None
        try:
            templates = self.get_public_templates()
        except Exception as e:
            logger.error(f"Failed to get artifact templates, Error: {e}")
        for template in templates:
            if template.template_data and template.template_data.name == artifact_template_name:
                resources_template = template.template_data.resources
                recommended_replica_resources = ReplicaResource(
                    cpu=resources_template.cpu,
                    ram_gb=resources_template.memory,
                    gpu=resources_template.gpu,
                    gpu_name=resources_template.gpu_name,
                )
                template_id = template.template_id
                break
        if not template_id:
            raise ValueError(f"Template with name {artifact_template_name} not found.")
        try: 
            artifact_id = self.create_artifact_from_template(template_id)
            self.wait_for_artifact_ready(artifact_id)
            return artifact_id, recommended_replica_resources
        except Exception as e:
            logger.error(f"Failed to create artifact from template, Error: {e}")
            raise e
        
    def create_artifact_for_serve_command_and_custom_model(self, template_name: str, artifact_name: str, serve_command: str, gpu_type: str, artifact_description: str = "", pre_download_model: str = "", env_parameters: Optional[Dict[str, Any]] = None) -> tuple[str, ReplicaResource]:
        """
        Create an artifact from a template and support custom model.
        :param artifact_template_name: The name of the template to use.
        :return: A tuple containing the artifact ID and the recommended replica resources.
        :rtype: tuple[str, ReplicaResource]
        """

        recommended_replica_resources = None
        picked_template = None
        try:
            templates = self.get_public_templates()
        except Exception as e:
            logger.error(f"Failed to get artifact templates, Error: {e}")
        for template in templates:
            if template.template_data and template.template_data.name == template_name:
                picked_template = template
                break
        if not picked_template:
            raise ValueError(f"Template with name {template_name} not found.")
        
        try:
            if gpu_type not in ["H100", "H200"]:
                raise ValueError("Only support H100 and H200 for now")
            
            type, env_vars, serve_args_dict = parse_server_command(serve_command)
            if type.lower() not in template_name.lower():
                raise ValueError(f"Template {template_name} does not support inference with {type}.")
            num_gpus = extract_gpu_num_from_serve_command(serve_args_dict)
            recommended_replica_resources = ReplicaResource(
                cpu=num_gpus * 16,
                ram_gb=num_gpus * 100,
                gpu=num_gpus,
                gpu_name=gpu_type,
            )
        except Exception as e:
            raise ValueError(f"Failed to parse serve command, Error: {e}")

        try:
            env_vars = []
            if picked_template.template_data and picked_template.template_data.env_parameters:
                env_vars = picked_template.template_data.env_parameters
            env_vars_map = {param.key: param for param in env_vars}
            if env_parameters:
                for key, value in env_parameters.items():
                    if key in ['GPU_TYPE', 'SERVE_COMMAND']:
                        continue
                    if key not in env_vars_map:
                        new_param = EnvParameter(key=key, value=value)
                        env_vars.append(new_param)
                        env_vars_map[key] = new_param
                    else:
                        env_vars_map[key].value = value
            env_vars.extend([
                EnvParameter(key="SERVE_COMMAND", value=serve_command),
                EnvParameter(key="GPU_TYPE", value=gpu_type),
            ])
            resp = self.create_artifact(artifact_name, artifact_description, deployment_type="template", template_id=picked_template.template_id, env_parameters=env_vars, artifact_volume_path=f"models/{pre_download_model}")
            # Assume Artifact is already with BuildStatus.SUCCESS status
            return resp.artifact_id, recommended_replica_resources
        except Exception as e:
            logger.error(f"Failed to create artifact from template, Error: {e}")
            raise e

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

        req = ResumableUploadLinkRequest(artifact_id=artifact_id, file_name=model_file_name, file_type=model_file_type)

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


    def upload_model_files_to_artifact(self, artifact_id: str, model_directory: str) -> None:
        """
        Upload model files to an existing artifact.

        :param artifact_id: The ID of the artifact to upload the model files to.
        :param model_directory: The path to the model directory.
        """

        # List all files in the model directory recursively
        model_file_paths = []
        for root, _, files in os.walk(model_directory):
            # Skip .cache folder
            if '.cache' in root.split(os.path.sep):
                continue
            for file in files:
                model_file_paths.append(os.path.join(root, file))

        def upload_file(model_file_path):
            self._validate_file_path(model_file_path)
            bigfile_upload_url_resp = self.artifact_client.get_bigfile_upload_url(
                ResumableUploadLinkRequest(artifact_id=artifact_id, file_name=os.path.basename(model_file_path))
            )
            FileUploadClient.upload_large_file(bigfile_upload_url_resp.upload_link, model_file_path)

        # Upload files in parallel with progress bar
        with tqdm(total=len(model_file_paths), desc="Uploading model files") as progress_bar:
            with logging_redirect_tqdm():
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = {executor.submit(upload_file, path): path for path in model_file_paths}
                    for future in concurrent.futures.as_completed(futures):
                        try:
                            future.result()
                        except Exception as e:
                            logger.error(f"Failed to upload file {futures[future]}, Error: {e}")
                        progress_bar.update(1)

    def create_artifact_with_model_files(
            self,
            artifact_name: str,
            artifact_file_path: str,
            model_directory: str,
            description: Optional[str] = "",
            tags: Optional[str] = None
    ) -> str:
        """
        Create a new artifact for a user and upload model files associated with the artifact.
        :param artifact_name: The name of the artifact.
        :param artifact_file_path: The path to the artifact file(Dockerfile+serve.py).
        :param model_directory: The path to the model directory.
        :param description: An optional description for the artifact.
        :param tags: Optional tags associated with the artifact, as a comma-separated string.
        :return: The `artifact_id` of the created artifact.
        """
        artifact_id = self.create_artifact_with_file(artifact_name, artifact_file_path, description, tags)
        logger.info(f"Artifact created: {artifact_id}")

        self.upload_model_files_to_artifact(artifact_id, model_directory)

        return artifact_id


    def wait_for_artifact_ready(self, artifact_id: str, timeout_s: int = 900) -> None:
        """
        Wait for an artifact to be ready.

        :param artifact_id: The ID of the artifact to wait for.
        :param timeout_s: The timeout in seconds.
        :return: None
        """
        start_time = time.time()
        while True:
            try:
                artifact = self.get_artifact(artifact_id)
                if artifact.build_status == BuildStatus.SUCCESS:
                    return
                elif artifact.build_status in [BuildStatus.FAILURE, BuildStatus.TIMEOUT, BuildStatus.CANCELLED]:
                    raise Exception(f"Artifact build failed, status: {artifact.build_status}")
            except Exception as e:
                logger.error(f"Failed to get artifact, Error: {e}")
            if time.time() - start_time > timeout_s:
                raise Exception(f"Artifact build takes more than {timeout_s // 60} minutes. Testing aborted.")
            time.sleep(10)

    
    def get_public_templates(self) -> List[Template]:
        """
        Fetch all artifact templates.

        :return: A list of Template objects.
        :rtype: List[Template]
        """
        return self.artifact_client.get_public_templates()
        

    def list_public_template_names(self) -> list[str]:
        """
        List all public templates.

        :return: A list of template names.
        :rtype: list[str]
        """
        template_names = []
        try: 
            templates = self.get_public_templates()
            for template in templates:
                if template.template_data and template.template_data.name:
                    template_names.append(template.template_data.name)
            return template_names
        except Exception as e:
            logger.error(f"Failed to get artifact templates, Error: {e}")
            return []


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
