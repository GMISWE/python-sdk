from datetime import datetime
from typing import List, Dict, Optional


class PortMapping:
    def __init__(self, container_port: int, exposed_port: int):
        self.container_port = container_port
        self.exposed_port = exposed_port


class HardwareTypeID(str): pass


class HardwareInstanceID(str): pass


class PodInstanceID(str): pass


class ClusterID(str): pass


class UserID(str): pass


class ContainerTemplateID(str): pass


class ReservationID(str): pass


class HostPathKey(str): pass


class LocalIP(str): pass


class PublicIP(str): pass


HOST_FS_KEY_LOCAL_STORAGE = HostPathKey("ls")
HOST_FS_KEY_NFS = HostPathKey("nfs")


class HostPathToContainerPathMapping:
    def __init__(self, host_path_key: HostPathKey, sub_path_under_host_path: str, container_path: str, read_only: bool):
        self.host_path_key = host_path_key
        self.sub_path_under_host_path = sub_path_under_host_path
        self.container_path = container_path
        self.read_only = read_only


class HardwareType:
    def __init__(self, hardware_type_id: HardwareTypeID, gpu_type: str, gpu_number: int, gpu_memory_gb: float,
                 cpu_number: float, main_memory_gb: float, local_disk_size_gb: float, ephemeral_storage_gb: float,
                 is_bare_metal: bool, available: bool, cluster_ids: List[ClusterID]):
        self.hardware_type_id = hardware_type_id
        self.gpu_type = gpu_type
        self.gpu_number = gpu_number
        self.gpu_memory_gb = gpu_memory_gb
        self.cpu_number = cpu_number
        self.main_memory_gb = main_memory_gb
        self.local_disk_size_gb = local_disk_size_gb
        self.ephemeral_storage_gb = ephemeral_storage_gb
        self.is_bare_metal = is_bare_metal
        self.available = available
        self.cluster_ids = cluster_ids


class HardwareInstanceInfo:
    def __init__(self, cluster_id: ClusterID, hardware_instance_id: HardwareInstanceID,
                 hardware_type_id: HardwareTypeID, hostname: str, host_local_storage_volume_path: str,
                 pod_instance_id: PodInstanceID, draining: bool, hardware_resource_spec: Optional[HardwareType],
                 dynamic_hardware_instance: bool, reservation_id: ReservationID):
        self.cluster_id = cluster_id
        self.hardware_instance_id = hardware_instance_id
        self.hardware_type_id = hardware_type_id
        self.hostname = hostname
        self.host_local_storage_volume_path = host_local_storage_volume_path
        self.pod_instance_id = pod_instance_id
        self.draining = draining
        self.hardware_resource_spec = hardware_resource_spec
        self.dynamic_hardware_instance = dynamic_hardware_instance
        self.reservation_id = reservation_id


class ContainerTemplate:
    def __init__(self, container_template_id: ContainerTemplateID, title: str, description: str):
        self.container_template_id = container_template_id
        self.title = title
        self.description = description


class LoginMethod:
    def __init__(self, ssh: str, jupyter_ip: str, ray_client_ip: str, ray_dashboard_ip: str):
        self.ssh = ssh
        self.jupyter_ip = jupyter_ip
        self.ray_client_ip = ray_client_ip
        self.ray_dashboard_ip = ray_dashboard_ip


class PodInstanceStatus(str):
    Preparing = "Preparing"
    Pending = "Pending"
    Starting = "Starting"
    Running = "Running"
    Terminating = "Terminating"
    Terminated = "Terminated"
    Unknown = "Unknown"
    Error = "Error"
    Failed = "Failed"
    Orphan = "Orphan"


class Event:
    def __init__(self, timestamp_microseconds: int, message: str, internal_message: str):
        self.timestamp_microseconds = timestamp_microseconds
        self.message = message
        self.internal_message = internal_message


class PodInstanceInfo:
    def __init__(self, user_id: UserID, pod_instance_id: PodInstanceID, pod_instance_name: str,
                 hardware_type_id: HardwareTypeID, container_template_id: ContainerTemplateID,
                 status: PodInstanceStatus, launching_timestamp_secs: int, running_timestamp_secs: int,
                 duration_hours: float, login_method: LoginMethod, events: List[Event], cluster_id: ClusterID,
                 hardware_resource_spec: Optional[HardwareType], port_mappings: List[PortMapping],
                 images: List['ContainerPullInfo'],
                 host_path_to_container_path_mappings: List[HostPathToContainerPathMapping], create_service: bool,
                 reservation_id: ReservationID, env_vars: Dict[str, str], launch_for_retail: bool):
        self.user_id = user_id
        self.pod_instance_id = pod_instance_id
        self.pod_instance_name = pod_instance_name
        self.hardware_type_id = hardware_type_id
        self.container_template_id = container_template_id
        self.status = status
        self.launching_timestamp_secs = launching_timestamp_secs
        self.running_timestamp_secs = running_timestamp_secs
        self.duration_hours = duration_hours
        self.login_method = login_method
        self.events = events
        self.cluster_id = cluster_id
        self.hardware_resource_spec = hardware_resource_spec
        self.port_mappings = port_mappings
        self.images = images
        self.host_path_to_container_path_mappings = host_path_to_container_path_mappings
        self.create_service = create_service
        self.reservation_id = reservation_id
        self.env_vars = env_vars
        self.launch_for_retail = launch_for_retail


class ContainerPullInfo:
    def __init__(self, image: str, auth_config_json: str, container_server_url: str, docker_hub_username: str,
                 docker_hub_access_token: str, gcp_service_account_key_json: str):
        self.image = image
        self.auth_config_json = auth_config_json
        self.container_server_url = container_server_url
        self.docker_hub_username = docker_hub_username
        self.docker_hub_access_token = docker_hub_access_token
        self.gcp_service_account_key_json = gcp_service_account_key_json


DockerHubrUrl = "https://index.docker.io/v1/"
NvidiaDockerHubUrl = "nvcr.io"
GcpArtifactRegistryUrlPattern = r'.*-docker\.pkg\.dev'


class PodInstanceQueryFilter:
    def __init__(self, status_filter: List[PodInstanceStatus], launching_timestamp_seconds_start: int,
                 launching_timestamp_seconds_end: int):
        self.status_filter = status_filter
        self.launching_timestamp_seconds_start = launching_timestamp_seconds_start
        self.launching_timestamp_seconds_end = launching_timestamp_seconds_end


class ResourceType(str):
    CPU = "cpu"
    RAM = "memory"
    EphemeralStorage = "ephemeral-storage"
    Storage = "storage"
    GPU = "gpu"
    NodeDown = "node_down"


class Unit(str):
    Count = "Count"
    GB = "GB"


class NodeResource:
    def __init__(self, resource_type: ResourceType, capacity: float, allocatable: float, allocated: float, usage: float,
                 unit: Unit):
        self.resource_type = resource_type
        self.capacity = capacity
        self.allocatable = allocatable
        self.allocated = allocated
        self.usage = usage
        self.unit = unit


class NamespaceResource:
    def __init__(self, resource_type: ResourceType, quota: float, allocated: float, usage: float, unit: Unit):
        self.resource_type = resource_type
        self.quota = quota
        self.allocated = allocated
        self.usage = usage
        self.unit = unit


UserName = str


class UserConfig:
    def __init__(self, user_name: UserName, k8s_config: str, k8s_namespaces: List[str]):
        self.user_name = user_name
        self.k8s_config = k8s_config
        self.k8s_namespaces = k8s_namespaces


class IpMapping: pass


class ClusterOptions:
    def __init__(self, cluster_id: ClusterID, user_configs: Dict[UserName, UserConfig],
                 ip_map: Dict[LocalIP, PublicIP]):
        self.cluster_id = cluster_id
        self.user_configs = user_configs
        self.ip_map = ip_map


class EndPointID(str): pass


class TTL_seconds(int): pass


class UserPreference:
    def __init__(self, block_list: List[str], preference_scale: float):
        self.block_list = block_list
        self.preference_scale = preference_scale


class EndPointConfig:
    def __init__(self, name: str, description: str, ttl: int, config_details: List['EndpointDetail'],
                 user_preference: UserPreference):
        self.name = name
        self.description = description
        self.ttl = ttl
        self.config_details = config_details
        self.user_preference = user_preference


class EndpointDetail:
    def __init__(self, ip: str, port: int, protocol: str, location: str, health_status: str, utilization_score: float,
                 last_health_check: datetime, time_availability: 'TimeRange', sticky_session: bool, cost: float):
        self.ip = ip
        self.port = port
        self.protocol = protocol
        self.location = location
        self.health_status = health_status
        self.utilization_score = utilization_score
        self.last_health_check = last_health_check
        self.time_availability = time_availability
        self.sticky_session = sticky_session
        self.cost = cost


class TimeRange:
    def __init__(self, start_hour: int, end_hour: int, weekdays: List[bool]):
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.weekdays = weekdays


class NamespaceStatus(str): pass


class Namespace:
    def __init__(self, name: str, status: NamespaceStatus):
        self.name = name
        self.status = status
