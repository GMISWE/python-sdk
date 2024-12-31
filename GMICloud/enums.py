from enum import Enum


class BuildStatus(str, Enum):
    INIT = "INIT"
    CREATED = "CREATED"
    BUILDING = "BUILDING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    TIMEOUT = "TIMEOUT"
    CANCELLED = "CANCELLED"

class TaskStatus(str, Enum):
    PENDING = "pending"
    DEPLOYING = "deploying"
    SCALING = "scaling"
    RUNNING = "running"
    ARCHIVED = "archived"

