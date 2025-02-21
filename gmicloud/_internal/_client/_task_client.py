import logging
from requests.exceptions import RequestException

from ._http_client import HTTPClient
from ._decorator import handle_refresh_token
from ._iam_client import IAMClient
from .._config import TASK_SERVICE_BASE_URL
from .._models import *

logger = logging.getLogger(__name__)


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
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Retrieves a task from the task service using the given task ID.

        :param task_id: The ID of the task to be retrieved.
        :return: An instance of Task containing the details of the retrieved task, or None if an error occurs.
        """
        try:
            response = self.client.get("/get_task", self.iam_client.get_custom_headers(), {"task_id": task_id})
            return Task.model_validate(response) if response else None
        except (RequestException, ValueError) as e:
            logger.error(f"Failed to retrieve task {task_id}: {e}")
            return None

    @handle_refresh_token
    def get_all_tasks(self) -> GetAllTasksResponse:
        """
        Retrieves all tasks from the task service.

        :return: An instance of GetAllTasksResponse containing the retrieved tasks.
        """
        try:
            response = self.client.get("/get_tasks", self.iam_client.get_custom_headers())
            if not response:
                logger.error("Empty response from /get_tasks")
                return GetAllTasksResponse(tasks=[])
            return GetAllTasksResponse.model_validate(response)
        except (RequestException, ValueError) as e:
            logger.error(f"Failed to retrieve all tasks: {e}")
            return GetAllTasksResponse(tasks=[])

    @handle_refresh_token
    def create_task(self, task: Task) -> Optional[CreateTaskResponse]:
        """
        Creates a new task using the provided task object.

        :param task: The Task object containing the details of the task to be created.
        :return: The response object containing created task details, or None if an error occurs.
        """
        try:
            response = self.client.post("/create_task", self.iam_client.get_custom_headers(), task.model_dump())
            return CreateTaskResponse.model_validate(response) if response else None
        except (RequestException, ValueError) as e:
            logger.error(f"Failed to create task: {e}")
            return None

    @handle_refresh_token
    def update_task_schedule(self, task: Task) -> bool:
        """
        Updates the schedule of an existing task.

        :param task: The Task object containing the updated task details.
        :return: True if update is successful, False otherwise.
        """
        try:
            response = self.client.put("/update_schedule", self.iam_client.get_custom_headers(), task.model_dump())
            return response is not None
        except RequestException as e:
            logger.error(f"Failed to update schedule for task {task.task_id}: {e}")
            return False

    @handle_refresh_token
    def start_task(self, task_id: str) -> bool:
        """
        Starts a task using the given task ID.

        :param task_id: The ID of the task to be started.
        :return: True if start is successful, False otherwise.
        """
        try:
            response = self.client.post("/start_task", self.iam_client.get_custom_headers(), {"task_id": task_id})
            return response is not None
        except RequestException as e:
            logger.error(f"Failed to start task {task_id}: {e}")
            return False

    @handle_refresh_token
    def stop_task(self, task_id: str) -> bool:
        """
        Stops a running task using the given task ID.

        :param task_id: The ID of the task to be stopped.
        :return: True if stop is successful, False otherwise.
        """
        try:
            response = self.client.post("/stop_task", self.iam_client.get_custom_headers(), {"task_id": task_id})
            return response is not None
        except RequestException as e:
            logger.error(f"Failed to stop task {task_id}: {e}")
            return False

    @handle_refresh_token
    def get_usage_data(self, start_timestamp: str, end_timestamp: str) -> Optional[GetUsageDataResponse]:
        """
        Retrieves the usage data of a task using the given task ID.

        :param start_timestamp: The start timestamp of the usage data.
        :param end_timestamp: The end timestamp of the usage data.
        :return: An instance of GetUsageDataResponse, or None if an error occurs.
        """
        try:
            response = self.client.get(
                "/get_usage_data",
                self.iam_client.get_custom_headers(),
                {"start_timestamp": start_timestamp, "end_timestamp": end_timestamp}
            )
            return GetUsageDataResponse.model_validate(response) if response else None
        except (RequestException, ValueError) as e:
            logger.error(f"Failed to retrieve usage data from {start_timestamp} to {end_timestamp}: {e}")
            return None

    @handle_refresh_token
    def archive_task(self, task_id: str) -> bool:
        """
        Archives a task using the given task ID.

        :param task_id: The ID of the task to be archived.
        :return: True if archiving is successful, False otherwise.
        """
        try:
            response = self.client.post("/archive_task", self.iam_client.get_custom_headers(), {"task_id": task_id})
            return response is not None
        except RequestException as e:
            logger.error(f"Failed to archive task {task_id}: {e}")
            return False
