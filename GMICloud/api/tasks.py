from GMICloud.http_client.http_client import HTTPClient
from GMICloud.config import TASK_SERVICE_BASE_URL
from GMICloud.models import Task, GetAllTasksResponse


class TaskClient:
    """
    A client for interacting with the task service API.

    This client provides methods to retrieve, create, update, and stop tasks
    through HTTP calls to the task service.
    """

    def __init__(self):
        """
        Initializes the TaskClient with the given base URL for the task service.
        """
        self.client = HTTPClient(TASK_SERVICE_BASE_URL)

    def get_all_tasks(self) -> GetAllTasksResponse:
        """
        Retrieves all tasks from the task service.

        :return: An instance of GetAllTasksResponse containing the retrieved tasks.
        :rtype: GetAllTasksResponse
        """
        result = self.client.post("/task-api/v1/get_tasks", "")

        return GetAllTasksResponse.model_validate(result)

    def create_task(self, task: Task):
        """
        Creates a new task using the provided task object.

        :param task: The Task object containing the details of the task to be created.
        """
        self.client.post("/task-api/v1/create_task", "", task.model_dump())

    def update_task_schedule(self, task: Task):
        """
        Updates the schedule of an existing task.

        :param task: The Task object containing the updated task details.
        """
        self.client.post("/task-api/v1/update_schedule", "", task.model_dump())

    def stop_task(self, task_id: str):
        """
        Stops a running task using the given task ID.

        :param task_id: The ID of the task to be stopped.
        """
        self.client.post("/task-api/v1/stop_task", "", {"task_id": task_id})
