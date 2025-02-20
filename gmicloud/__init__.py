import logging
import os

from ._internal._models import (
    Artifact,
    ArtifactData,
    ArtifactMetadata,
    Task,
    TaskOwner,
    TaskConfig,
    EndpointInfo,
    RayTaskConfig,
    TaskScheduling,
    ReplicaResource,
    OneOffScheduling,
    DailyScheduling,
    DailyTrigger,
    ArtifactTemplate,
)
from ._internal._enums import (
    BuildStatus,
    TaskEndpointStatus,
    TaskStatus
)
from .client import Client

__all__ = [
    "Client",
    "Artifact",
    "ArtifactData",
    "ArtifactMetadata",
    "Task",
    "TaskOwner",
    "TaskConfig",
    "EndpointInfo",
    "RayTaskConfig",
    "TaskScheduling",
    "ReplicaResource",
    "OneOffScheduling",
    "DailyScheduling",
    "DailyTrigger",
    "ArtifactTemplate",
    "BuildStatus",
    "TaskEndpointStatus",
]

# Configure logging
log_level = os.getenv("GMI_CLOUD_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
