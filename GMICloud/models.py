from typing import Optional
from datetime import datetime

from pydantic import BaseModel
from GMICloud.enums import BuildStatus, TaskStatus


class BigFileMetadata(BaseModel):
    """
    Metadata about a large file stored in a GCS bucket.
    """
    gcs_link: Optional[str]  # Link to the file stored in Google Cloud Storage.
    file_name: Optional[str]  # Name of the uploaded file.
    bucket_name: Optional[str]  # Name of the bucket where the file is stored.
    upload_time: Optional[datetime]  # Time when the file was uploaded.


class ArtifactMetadata(BaseModel):
    """
    Metadata information for an artifact.
    """
    user_id: Optional[str]  # The user ID associated with this artifact.
    artifact_name: Optional[str]  # Name of the artifact.
    artifact_description: Optional[str]  # Description of the artifact.
    artifact_tags: Optional[str]  # Comma-separated tags for categorizing the artifact.
    artifact_large_file_name: Optional[str]  # Name of the large file, if applicable.
    big_file_metadata: Optional[BigFileMetadata]  # Metadata for large files associated with this artifact.


class ArtifactData(BaseModel):
    """
    Data related to the artifact's creation, upload, and status.
    """
    artifact_type: Optional[str]  # The type of the artifact (e.g., model, dataset, etc.).
    upload_link: Optional[str]  # Direct link to upload the artifact.
    resumable_upload_link: Optional[str]  # Link for resuming a broken upload.
    artifact_link: Optional[str]  # Link to access the artifact.
    build_status: BuildStatus  # Status of the artifact build (e.g., in progress, succeeded, failed).
    build_id: Optional[str]  # ID of the build process associated with the artifact.
    create_at: Optional[datetime]  # Timestamp when the artifact was created.
    update_at: Optional[datetime]  # Timestamp when the artifact was last updated.


class Artifact(BaseModel):
    """
    Representation of an artifact, including its data and metadata.
    """
    artifact_id: str  # Unique identifier for the artifact.
    artifact_data: ArtifactData  # Data associated with the artifact.
    artifact_metadata: ArtifactMetadata  # Metadata describing the artifact.


class GetAllArtifactsResponse(BaseModel):
    """
    Response containing a list of all artifacts for a user.
    """
    artifacts: list[Artifact]  # List of Artifact objects.


class CreateArtifactRequest(BaseModel):
    """
    Request object to create a new artifact.
    """
    user_id: str  # The user ID creating the artifact.
    artifact_name: str  # The name of the artifact to create.
    artifact_description: str  # Description of the artifact.
    artifact_tags: str  # Tags for the artifact, separated by commas.


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
    artifact_id: Optional[str]  # ID of the artifact for which the upload URL is requested.
    file_name: Optional[str]  # Name of the file to upload.
    file_type: Optional[str]  # MIME type of the file.


class GetBigFileUploadUrlResponse(BaseModel):
    """
    Response containing a pre-signed upload URL for large files.
    """
    artifact_id: str  # ID of the artifact.
    upload_link: str  # Pre-signed upload URL for the file.


class TaskOwner(BaseModel):
    """
    Ownership information of a task.
    """
    user_id: str  # ID of the user owning the task.
    group_id: str  # ID of the group the user belongs to.
    service_account_id: str  # ID of the service account used to execute the task.


class ReplicaResource(BaseModel):
    """
    Resources allocated for task replicas.
    """
    cpu: Optional[int]  # Number of CPU cores allocated.
    ram_gb: Optional[int]  # Amount of RAM (in GB) allocated.
    gpu: Optional[int]  # Number of GPUs allocated.
    gpu_name: Optional[str]  # Type or model of the GPU allocated.


class RayTaskConfig(BaseModel):
    """
    Configuration settings for Ray tasks.
    """
    ray_version: Optional[str]  # Version of Ray used.
    artifact_id: Optional[str]  # Associated artifact ID.
    file_path: Optional[str]  # Path to the task file in storage.
    deployment_name: Optional[str]  # Name of the deployment.
    replica_resource: Optional[ReplicaResource]  # Resources allocated for task replicas.
    volume_mounts: Optional[dict]  # Configuration for mounted volumes.


class OneOffScheduling(BaseModel):
    """
    Scheduling configuration for a one-time trigger.
    """
    trigger_timestamp: int  # Timestamp when the task should start.
    min_replicas: int  # Minimum number of replicas to deploy.
    max_replicas: int  # Maximum number of replicas to deploy.


class DailyTrigger(BaseModel):
    """
    Scheduling configuration for daily task triggers.
    """
    timezone: Optional[str]  # Timezone for the trigger (e.g., "UTC").
    Hour: Optional[int]  # Hour of the day the task should start (0-23).
    minute: Optional[int]  # Minute of the hour the task should start (0-59).
    second: Optional[int]  # Second of the minute the task should start (0-59).
    min_replicas: Optional[int]  # Minimum number of replicas for this daily trigger.
    max_replicas: Optional[int]  # Maximum number of replicas for this daily trigger.


class DailyScheduling(BaseModel):
    """
    Configuration for daily scheduling triggers.
    """
    triggers: list[DailyTrigger]  # List of daily triggers.


class TaskScheduling(BaseModel):
    """
    Complete scheduling configuration for a task.
    """
    scheduling_oneoff: Optional[OneOffScheduling]  # One-time scheduling configuration.
    scheduling_daily: Optional[DailyScheduling]  # Daily scheduling configuration.


class TaskConfig(BaseModel):
    """
    Configuration data for a task.
    """
    ray_task_config: Optional[RayTaskConfig]  # Configuration for a Ray-based task.
    task_scheduling: Optional[TaskScheduling]  # Scheduling configuration for the task.
    create_timestamp: Optional[int]  # Timestamp when the task was created.
    last_update_timestamp: Optional[int]  # Timestamp when the task was last updated.


class TaskInfo(BaseModel):
    """
    Additional information about a task.
    """
    status: TaskStatus  # Current status of the task (e.g., running, stopped).
    endpoint: Optional[str]  # API endpoint exposed by the task, if applicable.


class Task(BaseModel):
    """
    Representation of a task.
    """
    task_id: Optional[str]  # Unique identifier for the task.
    owner: Optional[TaskOwner]  # Ownership information of the task.
    config: Optional[TaskConfig]  # Configuration data for the task.
    info: Optional[TaskInfo]  # Additional information about the task.


class GetAllTasksResponse(BaseModel):
    """
    Response containing a list of all tasks.
    """
    tasks: list[Task]  # List of tasks.
