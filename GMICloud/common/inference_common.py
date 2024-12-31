from typing import List, Dict


class PodID(str): pass


class JobID(str): pass


class TaskID(str): pass


class GroupID(str): pass


class ServiceAccountID(str): pass


class ArtifactID(str): pass


class TaskStatus(str): pass


class ReadinessStatus(str): pass


class EndpointStatus(str): pass


class UserRequestStatus(str): pass


class JobStatus(str): pass


class EndpointUrl(str): pass


class AccessMode(str): pass


REQUESTED = UserRequestStatus("requested")
SCALING = UserRequestStatus("scaling")
RUNNING = UserRequestStatus("running")
ARCHIVED = UserRequestStatus("archived")

TASK_PENDING = TaskStatus("pending")
TASK_DEPLOYING = TaskStatus("deploying")
TASK_SCALING = TaskStatus("scaling")
TASK_RUNNING = TaskStatus("running")
TASK_ARCHIVED = TaskStatus("archived")

READINESS_PENDING = ReadinessStatus("pending")
READINESS_READY = ReadinessStatus("ready")
READINESS_FAILED = ReadinessStatus("failed")

ENDPOINT_READY = EndpointStatus("ready")
ENDPOINT_NOT_READY = EndpointStatus("not_ready")
ENDPOINT_FAILED = EndpointStatus("failed")


class Owner:
    def __init__(self, owner_id: str):
        self.owner_id = owner_id


class TaskConfig:
    def __init__(self, config_id: str):
        self.config_id = config_id


class EndpointInfo:
    def __init__(self, endpoint: EndpointUrl):
        self.endpoint = endpoint


class Task:
    def __init__(self, task_id: TaskID, owner: Owner, config: TaskConfig, task_status: TaskStatus,
                 readiness_status: ReadinessStatus, endpoint_info: EndpointInfo):
        self.task_id = task_id
        self.owner = owner
        self.config = config
        self.task_status = task_status
        self.readiness_status = readiness_status
        self.endpoint_info = endpoint_info


class RayTaskConfig:
    def __init__(self, config_id: str):
        self.config_id = config_id


class JobConfig:
    def __init__(self, ray_task_config: RayTaskConfig, min_replicas: int, max_replicas: int, create_timestamp: int,
                 last_update_timestamp: int):
        self.ray_task_config = ray_task_config
        self.min_replicas = min_replicas
        self.max_replicas = max_replicas
        self.create_timestamp = create_timestamp
        self.last_update_timestamp = last_update_timestamp


class RayPodType(str):
    HeadPod = "head"
    WorkerPod = "worker"


class PodInstanceStatus(str): pass


class Event:
    def __init__(self, timestamp_microseconds: int, message: str, internal_message: str):
        self.timestamp_microseconds = timestamp_microseconds
        self.message = message
        self.internal_message = internal_message


class PodInfo:
    def __init__(self, pod_id: PodID, status: PodInstanceStatus, launching_timestamp_secs: int,
                 running_timestamp_secs: int, events: List[Event], ray_pod_type: RayPodType):
        self.pod_id = pod_id
        self.status = status
        self.launching_timestamp_secs = launching_timestamp_secs
        self.running_timestamp_secs = running_timestamp_secs
        self.events = events
        self.ray_pod_type = ray_pod_type


class ResourceType(str): pass


class NodeResource:
    def __init__(self, resource_type: ResourceType, capacity: float, allocatable: float, allocated: float, usage: float,
                 unit: str):
        self.resource_type = resource_type
        self.capacity = capacity
        self.allocatable = allocatable
        self.allocated = allocated
        self.usage = usage
        self.unit = unit


class ClusterResourceInfo:
    def __init__(self, node_resources: Dict[str, Dict[ResourceType, NodeResource]]):
        self.node_resources = node_resources


class JobInfo:
    def __init__(self, pods: List[PodInfo], num_replicas: int, max_replicas: int, endpoint: str, dashboard_url: str,
                 utilization_score: float, status: JobStatus):
        self.pods = pods
        self.num_replicas = num_replicas
        self.max_replicas = max_replicas
        self.endpoint = endpoint
        self.dashboard_url = dashboard_url
        self.utilization_score = utilization_score
        self.status = status


class Job:
    def __init__(self, job_id: JobID, task_id: TaskID, cluster_id: str, namespace: str, config: JobConfig,
                 info: JobInfo):
        self.job_id = job_id
        self.task_id = task_id
        self.cluster_id = cluster_id
        self.namespace = namespace
        self.config = config
        self.info = info


class RayReplicaResource:
    def __init__(self, resource_id: str):
        self.resource_id = resource_id


class VolumeMount:
    def __init__(self, mount_id: str):
        self.mount_id = mount_id


class TaskSchedulingOneoff:
    def __init__(self, trigger_timestamp: int, min_replicas: int, max_replicas: int):
        self.trigger_timestamp = trigger_timestamp
        self.min_replicas = min_replicas
        self.max_replicas = max_replicas


class TaskSchedulingDailyTrigger:
    def __init__(self, timezone: str, hour: int, minute: int, second: int, min_replicas: int, max_replicas: int):
        self.timezone = timezone
        self.hour = hour
        self.minute = minute
        self.second = second
        self.min_replicas = min_replicas
        self.max_replicas = max_replicas


class TaskSchedulingDaily:
    def __init__(self, triggers: List[TaskSchedulingDailyTrigger]):
        self.triggers = triggers


class TaskScheduling:
    def __init__(self, scheduling_oneoff: TaskSchedulingOneoff, scheduling_daily: TaskSchedulingDaily):
        self.scheduling_oneoff = scheduling_oneoff
        self.scheduling_daily = scheduling_daily


default_empty_scheduling = TaskScheduling(
    scheduling_oneoff=TaskSchedulingOneoff(
        trigger_timestamp=0,
        min_replicas=0,
        max_replicas=0,
    ),
    scheduling_daily=TaskSchedulingDaily(triggers=[])
)


def get_default_empty_scheduling() -> TaskScheduling:
    return default_empty_scheduling
