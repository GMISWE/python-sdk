from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel
from gmicloud._internal._enums import BuildStatus, TaskStatus, TaskEndpointStatus


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
    artifact_tags: Optional[List[str]] = ""  # Comma-separated tags for categorizing the artifact.
    artifact_volume_path: Optional[str] = ""  # Path to the volume where the artifact is stored.
    artifact_template_id: Optional[str] = ""  # The template ID used to create this artifact.


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
    artifact_tags: Optional[List[str]] = None  # Tags for the artifact, separated by commas.


class CreateArtifactResponse(BaseModel):
    """
    Response object after creating an artifact.
    """
    artifact_id: str  # ID of the newly created artifact.
    upload_link: str  # URL to upload the artifact data.


class GetBigFileUploadUrlRequest(BaseModel):
    """
    Request to generate a pre-signed URL for uploading large files.
    """
    artifact_id: Optional[str] = ""  # ID of the artifact for which the upload URL is requested.
    file_name: Optional[str] = ""  # Name of the file to upload.
    file_type: Optional[str] = ""  # MIME type of the file.


class GetBigFileUploadUrlResponse(BaseModel):
    """
    Response containing a pre-signed upload URL for large files.
    """
    artifact_id: str  # ID of the artifact.
    upload_link: str  # Pre-signed upload URL for the file.


class RebuildArtifactResponse(BaseModel):
    """
    Response object after rebuilding an artifact.
    """
    artifact_id: str  # ID of the rebuilt artifact.
    build_status: BuildStatus  # Status of the artifact build (e.g., in progress, succeeded, failed).


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


class GetPublicTemplatesResponse(BaseModel):
    """
    Response containing a list of artifact templates.
    """
    artifact_templates: list["ArtifactTemplate"]  # List of artifact templates.


class ArtifactTemplate(BaseModel):
    """
    Template for creating an artifact.
    """
    template_id: str  # Unique identifier for the artifact template.
    template_data: Optional["TemplateData"] = None  # Data for the artifact template.
    template_metadata: Optional["TemplateMetadata"] = None  # Metadata for the artifact template.


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

class TemplateData(BaseModel):
    """
    Data for an artifact template.
    """
    description: Optional[str] = ""  # Description of the artifact template.
    icon_link: Optional[str] = ""  # Link to the icon for the artifact template.
    image_link: Optional[str] = ""  # Link to the image for the artifact template.
    name: Optional[str] = ""  # Name of the artifact template.
    ray: Optional["RayContent"] = None  # Template for Ray-based artifacts.
    resources: Optional["ResourcesTemplate"] = None  # Resource allocation template.
    tags: Optional[List[str]] = None  # Tags associated with the artifact template.
    volume_path: Optional[str] = ""  # Path to the volume where the artifact is stored.


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
    user_id: str  # The user ID creating the artifact.
    artifact_template_id: str  # The ID of the artifact template to use.


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
    ray_version: Optional[str] = ""  # Version of Ray used.
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
    ray_task_config: Optional[RayTaskConfig] = None  # Configuration for a Ray-based task.
    task_scheduling: Optional[TaskScheduling] = None  # Scheduling configuration for the task.
    create_timestamp: Optional[int] = 0  # Timestamp when the task was created.
    last_update_timestamp: Optional[int] = 0  # Timestamp when the task was last updated.


class EndpointInfo(BaseModel):
    """
    Additional information about the task endpoint.
    """
    endpoint_status: Optional[TaskEndpointStatus] = None  # Current status of the task (e.g., running, stopped).
    endpoint_url: Optional[str] = ""  # URL for accessing the task endpoint.


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
    task_status: Optional[TaskStatus] = ""  # Status of the task.
    readiness_status: Optional[str] = ""  # Readiness status of the task.
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
