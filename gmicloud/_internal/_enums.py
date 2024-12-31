from enum import Enum


class BuildStatus(str, Enum):
    INIT = "INIT"
    CREATED = "CREATED"
    BUILDING = "BUILDING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    TIMEOUT = "TIMEOUT"
    CANCELLED = "CANCELLED"
    WORKING = "WORKING"
    QUEUED = "QUEUED"


class TaskEndpointStatus(str, Enum):
    UNKNOWN = ""
    PENDING = "pending"
    DEPLOYING = "deploying"
    SCALING = "scaling"
    RUNNING = "running"
    ARCHIVED = "archived"
    READY = "ready"
    UNREADY = "unready"
    NEW = "new"
