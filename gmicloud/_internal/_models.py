from typing import Optional, List, Union
from datetime import datetime

from pydantic import BaseModel
from gmicloud._internal._enums import *


class BigFileMetadata(BaseModel):
    """
    Metadata about a large file stored in a GCS bucket.
    """
    gcs_link: Optional[str] = ""  # Link to the file stored in Google Cloud Storage.
    file_name: Optional[str] = ""  # Name of the uploaded file.
    bucket_name: Optional[str] = ""  # Name of the bucket where the file is stored.
    upload_time: Optional[datetime]  # Time when the file was uploaded.


class ArtifactMetadata(BaseModel):
    """
    Metadata information for an artifact.
    """
    user_id: Optional[str] = ""  # The user ID associated with this artifact.
    artifact_name: Optional[str] = ""  # Name of the artifact.
    artifact_description: Optional[str] = ""  # Description of the artifact.
    artifact_tags: Optional[List[str]] = None  # Changed from List[str] with default to Optional[List[str]]
    artifact_volume_path: Optional[str] = ""  # Path to the volume where the artifact is stored.
    artifact_template_id: Optional[str] = ""  # The template ID used to create this artifact.
    artifact_icon_link: Optional[str] = ""  # Link to the icon for the artifact.
    is_public: Optional[bool] = False  # Indicates if the artifact is public.
    org_id: Optional[str] = ""  # Organization ID associated with this artifact.
    update_by: Optional[str] = ""  # User ID who last updated the artifact.


class ArtifactData(BaseModel):
    """
    Data related to the artifact's creation, upload, and status.
    """
    artifact_type: Optional[str] = ""  # The type of the artifact (e.g., model, DockerImage, etc.).
    artifact_link: Optional[str] = ""  # Link to access the artifact.
    artifact_resource: Optional[str] = ""  # Resource associated with the artifact (e.g., GCS link, S3 link).
    build_status: BuildStatus  # Status of the artifact build (e.g., in progress, succeeded, failed).
    build_error: Optional[str] = ""  # Error message if the build failed.
    build_file_name: Optional[str] = ""  # Name of the file used for the build.
    status: Optional[str] = ""  # Status of the artifact (e.g., active, inactive).
    build_id: Optional[str] = ""  # ID of the build process associated with the artifact.
    create_at: Optional[datetime]  # Timestamp when the artifact was created.
    update_at: Optional[datetime]  # Timestamp when the artifact was last updated.


class EnvParameter(BaseModel):
    """
    Environment parameter for an artifact.
    """
    key: str  # Key for the environment parameter.
    value: str  # Value for the environment parameter.


class ArtifactDetails(BaseModel):
    """
    Additional details for an artifact.
    """
    model_description: Optional[str] = ""  # Description of the model.


class ArtifactParameters(BaseModel):
    """
    Parameters for an artifact.
    """
    env_parameters: Optional[List[EnvParameter]] = None  # Environment parameters.
    model_parameters: Optional[List["ModelParameter"]] = None  # Model parameters.


class Artifact(BaseModel):
    """
    Representation of an artifact, including its data and metadata.
    """
    artifact_id: str  # Unique identifier for the artifact.
    artifact_link: Optional[str] = ""  # Link to access the artifact.
    build_file_name: Optional[str] = ""  # Name of the file used for the build.
    build_status: Optional[BuildStatus] = None  # Status of the artifact build (e.g., in progress, succeeded, failed).
    artifact_data: Optional[ArtifactData] = None  # Data associated with the artifact.
    artifact_metadata: Optional[ArtifactMetadata] = None  # Metadata describing the artifact.
    artifact_parameters: Optional[ArtifactParameters] = None  # Parameters for the artifact.
    big_files_metadata: Optional[List[BigFileMetadata]] = None  # Metadata for large files associated with the artifact.


class GetAllArtifactsResponse(BaseModel):
    """
    Response containing a list of all artifacts for a user.
    """
    artifacts: list[Artifact]  # List of Artifact objects.


class CreateArtifactRequest(BaseModel):
    """
    Request object to create a new artifact.
    """
    artifact_name: str  # The name of the artifact to create.
    artifact_description: Optional[str] = ""  # Description of the artifact.
    artifact_tags: Optional[List[str]] = None  # Tags for the artifact.
    deployment_type: Optional[str] = ""  # Deployment type
    template_id: Optional[str] = ""  # Template ID
    env_parameters: Optional[List["EnvParameter"]] = None  # Environment parameters.
    model_description: Optional[str] = ""  # Description of the model.
    model_parameters: Optional[List["ModelParameter"]] = None  # Parameters for the artifact.
    artifact_volume_path: Optional[str] = ""  # Path to the volume where the artifact is stored.


class CreateArtifactResponse(BaseModel):
    """
    Response object after creating an artifact.
    """
    artifact_id: str  # ID of the newly created artifact.
    upload_link: str  # URL to upload the artifact data.
    artifact_icon_link: Optional[str] = ""  # Link to the icon for the artifact.


class ResumableUploadLinkRequest(BaseModel):
    """
    Request to generate a pre-signed URL for uploading large files.
    """
    artifact_id: Optional[str] = ""  # ID of the artifact for which the upload URL is requested.
    file_name: Optional[str] = ""  # Name of the file to upload.
    file_type: Optional[str] = ""  # MIME type of the file.


class ResumableUploadLinkResponse(BaseModel):
    """
    Response containing a pre-signed upload URL for large files.
    """
    artifact_id: str  # ID of the artifact.
    upload_link: str  # Pre-signed upload URL for the file.


class RebuildArtifactRequest(BaseModel):
    """
    Request object for rebuilding an artifact.
    """
    artifact_id: str  # ID of the artifact to rebuild.


class RebuildArtifactResponse(BaseModel):
    """
    Response object after rebuilding an artifact.
    """
    artifact_id: str  # ID of the rebuilt artifact.
    build_status: BuildStatus  # Status of the artifact build (e.g., in progress, succeeded, failed).


class EndpointInfo(BaseModel):
    """
    Additional information about the task endpoint.
    """
    endpoint_status: Optional[TaskEndpointStatus] = None  # Current status of the task (e.g., running, stopped).
    endpoint_url: Optional[str] = ""  # URL for accessing the task endpoint.


class GetAllArtifactsWithEndpointsResponse(BaseModel):
    """
    Response containing a list of all artifacts with their endpoints.
    """
    artifact_id: str  # Unique identifier for the artifact.
    artifact_data: Optional[ArtifactData] = None  # Data associated with the artifact.
    artifact_metadata: Optional[ArtifactMetadata] = None  # Metadata describing the artifact.
    artifact_details: Optional[ArtifactDetails] = None  # Additional details about the artifact.
    artifact_parameters: Optional[ArtifactParameters] = None  # Parameters for the artifact.
    big_files_metadata: Optional[List[BigFileMetadata]] = None  # Metadata for large files.
    endpoints: Optional[List[EndpointInfo]] = None  # Endpoints associated with the artifact.


class GetArtifactResponse(BaseModel):
    """
    Response containing the details of an artifact.
    """
    artifact_id: str  # Unique identifier for the artifact.
    artifact_link: Optional[str] = ""  # Link to access the artifact.
    artifact_resource: Optional[str] = ""  # Resource associated with the artifact.
    build_file_name: Optional[str] = ""  # Name of the file used for the build.
    build_status: Optional[str] = ""  # Status of the artifact build.
    artifact_metadata: Optional[ArtifactMetadata] = None  # Metadata describing the artifact.
    artifact_parameters: Optional[ArtifactParameters] = None  # Parameters for the artifact.
    big_files_metadata: Optional[List[BigFileMetadata]] = None  # Metadata for large files.


class GetPublicArtifactsResponse(BaseModel):
    """
    Response containing public artifact details.
    """
    artifact_id: str  # Unique identifier for the artifact.
    artifact_data: Optional[ArtifactData] = None  # Data associated with the artifact.
    artifact_metadata: Optional[ArtifactMetadata] = None  # Metadata describing the artifact.
    artifact_details: Optional[ArtifactDetails] = None  # Additional details about the artifact.
    artifact_parameters: Optional[ArtifactParameters] = None  # Parameters for the artifact.
    endpoints: Optional[List[EndpointInfo]] = None  # Endpoints associated with the artifact.


class UpdateArtifactRequestBody(BaseModel):
    """
    Request object for updating an artifact.
    """
    artifact_name: Optional[str] = ""  # The name of the artifact.
    artifact_description: Optional[str] = ""  # Description of the artifact.
    artifact_tags: Optional[List[str]] = None  # Tags for the artifact.
    env_parameters: Optional[List[EnvParameter]] = None  # Environment parameters.
    model_description: Optional[str] = ""  # Description of the model.
    model_parameters: Optional[List["ModelParameter"]] = None  # Parameters for the artifact.
    need_update_icon: Optional[bool] = False  # Whether to update the artifact icon.


class UpdateArtifactResponse(BaseModel):
    """
    Response object after updating an artifact.
    """
    artifact_id: str  # ID of the updated artifact.
    status: str  # Status of the update operation.
    artifact_icon_link: Optional[str] = ""  # Link to the icon for the artifact.


class GetTemplatesResponse(BaseModel):
    """
    Response containing a list of artifact templates.
    """
    artifact_templates: list["Template"]  # List of artifact templates.


class Template(BaseModel):
    """
    Template for creating an artifact.
    """
    template_id: str  # Unique identifier for the artifact template.
    template_data: Optional["TemplateData"] = None  # Data for the artifact template.
    template_metadata: Optional["TemplateMetadata"] = None  # Metadata for the artifact template.


class DeleteArtifactResponse(BaseModel):
    """
    Response object after deleting an artifact.
    """
    artifact_id: str  # ID of the deleted artifact.
    delete_at: Optional[datetime] = None  # Timestamp when the artifact was deleted.
    status: Optional[str] = ""  # Status of the deletion process.


class DeleteBigfileRequest(BaseModel):
    """
    Request to delete a large file associated with an artifact.
    """
    artifact_id: str  # ID of the artifact for which the large file is to be deleted.
    file_name: str  # Name of the large file to delete.


class DeleteBigfileResponse(BaseModel):
    """
    Response object after deleting a large file.
    """
    artifact_id: str  # ID of the artifact.
    file_name: str  # Name of the deleted file.
    status: Optional[str] = ""  # Status of the deletion process.


class TemplateMetadata(BaseModel):
    """
    Metadata for an artifact template.
    """
    create_at: Optional[str] = None  # Timestamp when the template was created.
    create_by: Optional[str] = ""  # ID of the user who created the template.
    create_by_org_id: Optional[str] = ""  # ID of the organization to which the user belongs.
    is_public: Optional[bool] = False  # Indicates if the template is public.
    update_at: Optional[str] = None  # Timestamp when the template was last updated.
    update_by: Optional[str] = ""  # ID of the user who last updated the template.
    status: Optional[str] = ""  # Status of the template.


class TemplateData(BaseModel):
    """
    Data for an artifact template.
    """
    description: Optional[str] = ""  # Description of the artifact template.
    icon_link: Optional[str] = ""  # Link to the icon for the artifact template.
    image_link: Optional[str] = ""  # Link to the image for the artifact template.
    model_parameters: Optional[List["ModelParameter"]] = None  # Parameters for the artifact template.
    name: Optional[str] = ""  # Name of the artifact template.
    ray: Optional["RayContent"] = None  # Template for Ray-based artifacts.
    resources: Optional["ResourcesTemplate"] = None  # Resource allocation template.
    tags: Optional[List[str]] = None  # Tags associated with the artifact template.
    volume_path: Optional[str] = ""  # Path to the volume where the artifact is stored.
    env_parameters: Optional[List["EnvParameter"]] = None  # Added missing field


class ModelParameter(BaseModel):
    """
    Parameter for an artifact template.
    """
    category: Optional[str] = ""  # Category of the parameter.
    display_name: Optional[str] = ""  # Display name of the parameter.
    key: Optional[str] = ""  # Key for the parameter.
    max: Optional[float] = 0  # Maximum value for the parameter.
    min: Optional[float] = 0  # Minimum value for the parameter.
    step: Optional[float] = 0  # Step value for the parameter.
    type: Optional[ModelParameterType] = ModelParameterType.TEXT  # Type of the parameter (e.g., numeric, bool, text).
    value: Optional[Union[int, float, bool, str]] = ""  # Default value for the parameter.

class RayContent(BaseModel):
    deployment_name: Optional[str] = ""  # Name of the deployment.
    file_path: Optional[str] = ""  # Path to the task file in storage.


class ResourcesTemplate(BaseModel):
    cpu: Optional[int] = 0  # Number of CPU cores allocated.
    memory: Optional[int] = 0  # Amount of RAM (in GB) allocated.
    gpu: Optional[int] = 0  # Number of GPUs allocated.
    gpu_name: Optional[str] = ""  # Type the GPU allocated.


class CreateArtifactFromTemplateRequest(BaseModel):
    """
    Request object to create a new artifact from a template.
    """
    # user_id: str  # The user ID creating the artifact.
    artifact_template_id: str  # The ID of the artifact template to use.
    env_parameters: Optional[List["EnvParameter"]] = None  # Environment parameters.


class CreateArtifactFromTemplateResponse(BaseModel):
    """
    Response object after creating an artifact from a template
    """
    artifact_id: str  # ID of the newly created artifact.
    status: str  # Status of the creation process.


class TaskOwner(BaseModel):
    """
    Ownership information of a task.
    """
    user_id: Optional[str] = ""  # ID of the user owning the task.
    group_id: Optional[str] = ""  # ID of the group the user belongs to.
    service_account_id: Optional[str] = ""  # ID of the service account used to execute the task.


class ReplicaResource(BaseModel):
    """
    Resources allocated for task replicas.
    """
    cpu: Optional[int] = 0  # Number of CPU cores allocated.
    ram_gb: Optional[int] = 0  # Amount of RAM (in GB) allocated.
    gpu: Optional[int] = 0  # Number of GPUs allocated.
    gpu_name: Optional[str] = ""  # Type or model of the GPU allocated.


class VolumeMount(BaseModel):
    """
    Configuration for mounting volumes in a container.
    """
    access_mode: Optional[str] = ""  # Access mode for the volume (e.g., read-only, read-write).
    capacity_GB: Optional[int] = ""  # Capacity of the volume in GB.
    host_path: Optional[str] = ""  # Path on the host machine where the volume is mounted.
    mount_path: Optional[str] = ""  # Path where the volume is mounted in the container.


class RayTaskConfig(BaseModel):
    """
    Configuration settings for Ray tasks.
    """
    artifact_id: Optional[str] = ""  # Associated artifact ID.
    ray_cluster_image: Optional[str] = ""  # Docker image for the Ray cluster.
    file_path: Optional[str] = ""  # Path to the task file in storage.
    deployment_name: Optional[str] = ""  # Name of the deployment.
    replica_resource: Optional[ReplicaResource] = None  # Resources allocated for task replicas.
    volume_mounts: Optional[List[VolumeMount]] = None  # Configuration for mounted volumes.


class OneOffScheduling(BaseModel):
    """
    Scheduling configuration for a one-time trigger.
    """
    trigger_timestamp: Optional[int] = 0  # Timestamp when the task should start.
    min_replicas: Optional[int] = 0  # Minimum number of replicas to deploy.
    max_replicas: Optional[int] = 0  # Maximum number of replicas to deploy.


class DailyTrigger(BaseModel):
    """
    Scheduling configuration for daily task triggers.
    """
    timezone: Optional[str] = ""  # Timezone for the trigger (e.g., "UTC").
    Hour: Optional[int] = 0  # Hour of the day the task should start (0-23).
    minute: Optional[int] = 0  # Minute of the hour the task should start (0-59).
    second: Optional[int] = 0  # Second of the minute the task should start (0-59).
    min_replicas: Optional[int] = 0  # Minimum number of replicas for this daily trigger.
    max_replicas: Optional[int] = 0  # Maximum number of replicas for this daily trigger.


class DailyScheduling(BaseModel):
    """
    Configuration for daily scheduling triggers.
    """
    triggers: Optional[list[DailyTrigger]] = None  # List of daily triggers.


class TaskScheduling(BaseModel):
    """
    Complete scheduling configuration for a task.
    """
    scheduling_oneoff: Optional[OneOffScheduling] = None  # One-time scheduling configuration.
    scheduling_daily: Optional[DailyScheduling] = None  # Daily scheduling configuration.


class TaskConfig(BaseModel):
    """
    Configuration data for a task.
    """
    task_name: Optional[str] = ""  # Name of the task.
    ray_task_config: Optional[RayTaskConfig] = None  # Configuration for a Ray-based task.
    task_scheduling: Optional[TaskScheduling] = None  # Scheduling configuration for the task.
    create_timestamp: Optional[int] = 0  # Timestamp when the task was created.
    last_update_timestamp: Optional[int] = 0  # Timestamp when the task was last updated.


class UserPreference(BaseModel):
    """
    User preference for a task.
    """
    block_list: Optional[List[str]] = None  # List of tasks to exclude.
    preference_scale: Optional[int] = 0  # Scale of user preference.


class Task(BaseModel):
    """
    Representation of a task.
    """
    task_id: Optional[str] = None  # Unique identifier for the task.
    owner: Optional[TaskOwner] = None  # Ownership information of the task.
    config: Optional[TaskConfig] = None  # Configuration data for the task.
    endpoint_info: Optional[EndpointInfo] = None  # Additional information about the task endpoint.
    cluster_endpoints: Optional[List[EndpointInfo]] = None  # Endpoints for the task cluster.
    task_status: Optional[TaskStatus] = None  # Status of the task.
    readiness_status: Optional[str] = None  # Readiness status of the task.
    user_preference: Optional[UserPreference] = None  # User preference for the task.


class GetAllTasksResponse(BaseModel):
    """
    Response containing a list of all tasks.
    """
    tasks: Optional[list[Task]] = None  # List of tasks.


class CreateTaskResponse(BaseModel):
    task: Task  # The created task.
    upload_link: str  # URL to upload the task data.


class AuthTokenRequest(BaseModel):
    """
    Request object for user login.
    """
    email: str  # User email.
    password: str  # User password.


class AuthTokenResponse(BaseModel):
    """
    Response object for user login.
    """
    authToken: str  # Access token for the user session.
    is2FARequired: bool  # Indicates if 2FA is required for the user.


class CreateSessionRequest(BaseModel):
    """
    Request object for creating a user session.
    """
    type: str  # Type of the session (e.g., native).
    authToken: str  # Access token for the user session.
    otpCode: Optional[str]  # 2FA code for the user session.


class CreateSessionResponse(BaseModel):
    """
    Response object for creating a user session.
    """
    accessToken: str  # Access token for the user session.
    refreshToken: str  # Refresh token for the user session.


class GPUUsage(BaseModel):
    """
    GPU usage data for a task.
    """
    geo_location: Optional[str] = ""  # Location of the GPU.
    gpu_count: Optional[int] = ""  # Number of GPUs.
    gpu_type: Optional[str] = ""  # Type of GPU.


class Usage(BaseModel):
    """
    Usage data for a task.
    """
    user_id: Optional[str] = ""  # ID of the user.
    task_id: Optional[str] = ""  # ID of the task.
    gpu_usage_list: Optional[List[GPUUsage]] = None  # List of GPU usage data.
    replica_count: Optional[int] = 0  # Number of replicas.
    timestamp: Optional[int] = 0  # Timestamp of the usage data.


class GetUsageDataResponse(BaseModel):
    """
    Response containing the usage data of a task.
    """
    usage_data: list[Usage] = None  # List of usage data for the task.


class LoginRequest(BaseModel):
    """
    Request object for user login.
    """
    email: str  # User email.
    password: str  # User password.


class User(BaseModel):
    """
    User information.
    """
    id: Optional[str] = ""  # User ID.
    email: Optional[str] = ""  # User email.
    firstName: Optional[str] = ""  # User first name.
    lastName: Optional[str] = ""  # User last name.


class Organization(BaseModel):
    """
    Organization information.
    """
    id: Optional[str] = ""  # Organization ID.
    role: Optional[str] = ""  # Organization role.


class ProfileResponse(BaseModel):
    """
    Response object for user profile.
    """
    user: User  # User information.
    organization: Organization  # Organization information.


class CreateAPIKeyRequest(BaseModel):
    """
    Request object for creating an API key.
    """
    name: str  # Name of the API key.
    type: Optional[str] = ""  # Type of the API key.
    expiresAt: Optional[int] = 0  # Expiration timestamp for the API key.


class CreateAPIKeyResponse(BaseModel):
    """
    Response object for creating an API key.
    """
    key: str  # The created API key.


class APIKey(BaseModel):
    """
    API key information.
    """
    id: Optional[str] = ""  # API key ID.
    name: Optional[str] = ""  # API key name.
    type: Optional[str] = ""  # API key type.
    partialKey: Optional[str] = ""  # Partial key for the API key.
    expiresAt: Optional[int] = 0  # Expiration timestamp for the API key.
    createdAt: Optional[int] = 0  # Creation timestamp for the API key.
    owner: Optional[User] = None  # Owner of the API key.


class GetAPIKeysResponse(BaseModel):
    """
    Response object for getting a list of API keys.
    """
    keys: list[APIKey]  # List of API keys.


class GetSelfAPIKeyResponse(BaseModel):
    """
    Response object for getting the API key of the current user.
    """
    key: APIKey  # The API key of the current user.
    organization: Optional[Organization] = None  # Organization information.



# ----------------- video models -----------------

class SubmitRequestRequest(BaseModel):
    """
    The request body for submits a new asynchronous request 
    """
    model: str
    payload: dict


class SubmitRequestResponse(BaseModel):
    """
    Represents the response body for a submitted request.
    """
    created_at: Optional[int] = 0
    model: Optional[str] = ""
    queued_at: Optional[int] = 0
    request_id: Optional[str] = ""
    status: Optional[RequestStatus] = None
    updated_at: Optional[int] = 0


class GetRequestResponse(BaseModel):
    """
    Response object for getting a specific request.
    """
    created_at: Optional[int] = 0
    is_public: Optional[bool] = False
    model: Optional[str] = ""
    org_id: Optional[str] = ""
    outcome: Optional[dict] = {}
    payload: Optional[dict] = {}
    queued_at: Optional[int] = 0
    qworker_id: Optional[str] = ""
    request_id: Optional[str] = ""
    status: Optional[RequestStatus] = None
    updated_at: Optional[int] = 0


class ListUserRequestsResponse(BaseModel):
    """
    Represents the response body for listing user requests.
    """
    requests: List[GetRequestResponse]
    total: Optional[int] = 0  # Total number of requests available for the user.


class PriceInfo(BaseModel):
    """
    Represents pricing information for a model.
    """
    price: Optional[int] = 0
    pricing_type: Optional[str] = ""
    unit: Optional[str] = ""


class GetModelResponse(BaseModel):
    """
    Represents the response body for a specific model.
    """
    background_image_url: Optional[str] = ""
    brief_description: Optional[str] = ""
    created_at: Optional[int] = 0
    detailed_description: Optional[str] = ""
    external_api_endpoint: Optional[str] = ""
    external_api_url: Optional[str] = ""
    external_provider: Optional[str] = ""
    host_type: Optional[HostType] = HostType.DEFAULT
    icon_link: Optional[str] = ""
    internal_parameters: Optional[dict] = {}
    modalities: Optional[dict] = {}
    model: Optional[str] = ""
    model_type: Optional[str] = ""
    org_id: Optional[str] = ""
    parameters: Optional[list] = []
    price_info: Optional[PriceInfo] = None
    qworkers: Optional[int] = 0
    tags: Optional[list[str]] = []
    updated_at: Optional[int] = 0