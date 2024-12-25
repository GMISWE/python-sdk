from typing import List

from ...common import Owner, TaskConfig, UserPreference, Task, TaskID, TaskScheduling


class CreateTaskRequest:
    def __init__(self, owner: Owner, config: TaskConfig, user_preference: UserPreference):
        self.owner = owner
        self.config = config
        self.user_preference = user_preference


class CreateTaskResponse:
    def __init__(self, task: Task, upload_link: str):
        self.task = task
        self.upload_link = upload_link


class GetTaskRequest:
    def __init__(self, task_id: TaskID):
        self.task_id = task_id


class GetTasksResponse:
    def __init__(self, tasks: List[Task]):
        self.tasks = tasks


class UpdateTaskScheduleRequest:
    def __init__(self, task_id: TaskID, task_scheduling: TaskScheduling):
        self.task_id = task_id
        self.task_scheduling = task_scheduling


class UpdateTaskScheduleResponse:
    pass


class StopTaskRequest:
    def __init__(self, task_id: TaskID):
        self.task_id = task_id
