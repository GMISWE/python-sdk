from ._http_client import HTTPClient
from ._decorator import handle_refresh_token
from ._iam_client import IAMClient
from .._config import TASK_SERVICE_BASE_URL
from .._models import *
from .._constants import ACCESS_TOKEN_HEADER, CLIENT_ID_HEADER


class TaskClient:
    """
    A client for interacting with the task service API.

    This client provides methods to retrieve, create, update, and stop tasks
    through HTTP calls to the task service.
    """

    def __init__(self, iam_client: IAMClient):
        """
        Initializes the TaskClient with the given base URL for the task service.
        """
        self.client = HTTPClient(TASK_SERVICE_BASE_URL)
        self.iam_client = iam_client

    @handle_refresh_token
    def get_task(self, task_id: str) -> Task:
        """
        Retrieves a task from the task service using the given task ID.

        :param task_id: The ID of the task to be retrieved.
        :return: An instance of Task containing the details of the retrieved task.
        :rtype: Task
        """
        custom_headers = {
            ACCESS_TOKEN_HEADER: self.iam_client.get_access_token(),
            CLIENT_ID_HEADER: self.iam_client.get_client_id()
        }
        result = self.client.get("/get_task", custom_headers, {"task_id": task_id})

        return Task.model_validate(result)

    @handle_refresh_token
    def get_all_tasks(self) -> GetAllTasksResponse:
        """
        Retrieves all tasks from the task service.

        :return: An instance of GetAllTasksResponse containing the retrieved tasks.
        :rtype: GetAllTasksResponse
        """
        custom_headers = {
            ACCESS_TOKEN_HEADER: self.iam_client.get_access_token(),
            CLIENT_ID_HEADER: self.iam_client.get_client_id()
        }
        result = self.client.get("/get_tasks", custom_headers)
        if not result:
            return GetAllTasksResponse(tasks=[])

        return GetAllTasksResponse.model_validate(result)

    @handle_refresh_token
    def create_task(self, task: Task) -> CreateTaskResponse:
        """
        Creates a new task using the provided task object.

        :param task: The Task object containing the details of the task to be created.
        """
        custom_headers = {
            ACCESS_TOKEN_HEADER: self.iam_client.get_access_token(),
            CLIENT_ID_HEADER: self.iam_client.get_client_id()
        }

        result = self.client.post("/create_task", custom_headers, task.model_dump())

        return CreateTaskResponse.model_validate(result)

    @handle_refresh_token
    def update_task_schedule(self, task: Task):
        """
        Updates the schedule of an existing task.

        :param task: The Task object containing the updated task details.
        """
        custom_headers = {
            ACCESS_TOKEN_HEADER: self.iam_client.get_access_token(),
            CLIENT_ID_HEADER: self.iam_client.get_client_id()
        }
        self.client.put("/update_schedule", custom_headers, task.model_dump())

    @handle_refresh_token
    def start_task(self, task_id: str):
        """
        Starts a task using the given task ID.

        :param task_id: The ID of the task to be started.
        """
        custom_headers = {
            ACCESS_TOKEN_HEADER: self.iam_client.get_access_token(),
            CLIENT_ID_HEADER: self.iam_client.get_client_id()
        }
        self.client.post("/start_task", custom_headers, {"task_id": task_id})

    @handle_refresh_token
    def stop_task(self, task_id: str):
        """
        Stops a running task using the given task ID.

        :param task_id: The ID of the task to be stopped.
        """
        custom_headers = {
            ACCESS_TOKEN_HEADER: self.iam_client.get_access_token(),
            CLIENT_ID_HEADER: self.iam_client.get_client_id()
        }
        self.client.post("/stop_task", custom_headers, {"task_id": task_id})

    @handle_refresh_token
    def get_usage_data(self, start_timestamp: str, end_timestamp: str) -> GetUsageDataResponse:
        """
        Retrieves the usage data of a task using the given task ID.

        :param start_timestamp: The start timestamp of the usage data.
        :param end_timestamp: The end timestamp of the usage data.
        """
        custom_headers = {
            ACCESS_TOKEN_HEADER: self.iam_client.get_access_token(),
            CLIENT_ID_HEADER: self.iam_client.get_client_id()
        }
        result = self.client.get("/get_usage_data", custom_headers,
                                 {"start_timestamp": start_timestamp, "end_timestamp": end_timestamp})

        return result

    @handle_refresh_token
    def archive_task(self, task_id: str):
        """
        Archives a task using the given task ID.

        :param task_id: The ID of the task to be archived.
        """
        custom_headers = {
            ACCESS_TOKEN_HEADER: self.iam_client.get_access_token(),
            CLIENT_ID_HEADER: self.iam_client.get_client_id()
        }
        self.client.post("/archive_task", custom_headers, {"task_id": task_id})
