import os
from typing import List

from GMICloud.api.tasks import TaskClient
from GMICloud.models import Task


class TaskManager:
    """
    TaskManager handles operations related to tasks, including creation, scheduling, and stopping tasks.
    """
    def __init__(self):
        """
        Initialize the TaskManager instance and the associated TaskClient.
        """
        self.task_client = TaskClient()

    def get_all_tasks(self) -> List[Task]:
        """
        Retrieve a list of all tasks available in the system.

        :return: A list of `Task` objects.
        """
        return self.task_client.get_all_tasks().tasks

    def create_task(self, task: Task):
        """
        Create a new task.

        :param task: A `Task` object containing the details of the task to be created.
        :return: None
        :raises ValueError: If `task` is None.
        """
        self._validate_task(task)
        self.task_client.create_task(task)

    def create_task_with_file(self, file_path: str):
        """
        Create a new task from a file. The file should contain a valid task definition.

        :param file_path: The path to the file containing the task data.
        :return: None
        :raises ValueError: If the `file_path` is invalid or the file cannot be read.
        """
        task = self._read_file_and_parse_task(file_path)
        self.create_task(task)

    def update_task_schedule(self, task: Task):
        """
        Update the schedule of an existing task.

        :param task: A `Task` object containing the updated schedule details.
        :return: None
        :raises ValueError: If `task` is None.
        """
        self._validate_task(task)
        self.task_client.update_task_schedule(task)

    def update_task_schedule_with_file(self, file_path: str):
        """
        Update the schedule of a task using data from a file. The file should contain a valid task definition.

        :param file_path: The path to the file containing the updated task schedule data.
        :return: None
        :raises ValueError: If the `file_path` is invalid or the file cannot be read.
        """
        task = self._read_file_and_parse_task(file_path)
        self.update_task_schedule(task)

    def stop_task(self, task_id: str):
        """
        Stop a task by its ID.

        :param task_id: The ID of the task to be stopped.
        :return: None
        :raises ValueError: If `task_id` is invalid (None or empty string).
        """
        if not task_id or not task_id.strip():
            raise ValueError("Task ID is required and cannot be empty.")

        self.task_client.stop_task(task_id)

    @staticmethod
    def _validate_task(task: Task) -> None:
        """
        Validate a Task object.

        :param task: The Task object to validate.
        :raises ValueError: If `task` is None.
        """
        if task is None:
            raise ValueError("Task object is required and cannot be None.")

    @staticmethod
    def _validate_file_path(file_path: str) -> None:
        """
        Validate the file path.

        :param file_path: The file path to validate.
        :raises ValueError: If `file_path` is None, empty, or does not exist.
        """
        if not file_path or not file_path.strip():
            raise ValueError("File path is required and cannot be empty.")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

    def _read_file_and_parse_task(self, file_path: str) -> Task:
        """
        Read a file and parse it into a Task object.

        :param file_path: The path to the file to be read.
        :return: A `Task` object parsed from the file content.
        :raises ValueError: If the file is invalid or cannot be parsed.
        """
        self._validate_file_path(file_path)

        with open(file_path, "rb") as file:
            file_data = file.read()

        try:
            task = Task.model_validate(file_data)  # Ensure Task has a static method for model validation.
        except Exception as e:
            raise ValueError(f"Failed to parse Task from file: {file_path}. Error: {str(e)}")

        return task