import os
import time
import logging

from typing import Optional

from ._internal._client._iam_client import IAMClient
from ._internal._manager._artifact_manager import ArtifactManager
from ._internal._manager._task_manager import TaskManager
from ._internal._manager._iam_manager import IAMManager
from ._internal._enums import BuildStatus
from ._internal._models import Task, TaskConfig, RayTaskConfig, TaskScheduling, ReplicaResource

logger = logging.getLogger(__name__)


class Client:
    def __init__(self, client_id: Optional[str] = "", email: Optional[str] = "", password: Optional[str] = ""):
        if not client_id or not client_id.strip():
            client_id = os.getenv("GMI_CLOUD_CLIENT_ID")
        if not email or not email.strip():
            email = os.getenv("GMI_CLOUD_EMAIL")
        if not password or not password.strip():
            password = os.getenv("GMI_CLOUD_PASSWORD")

        if not client_id:
            raise ValueError("Client ID must be provided.")
        if not email:
            raise ValueError("Email must be provided.")
        if not password:
            raise ValueError("Password must be provided.")

        self.iam_client = IAMClient(client_id, email, password)
        self.iam_client.login()

        # Managers are lazily initialized through private attributes
        self._artifact_manager = None
        self._task_manager = None
        self._iam_manager = None

    def create_task_from_artifact_template(self, artifact_template_id: str, task_scheduling: TaskScheduling) -> Task:
        """
        Create a task from a template.

        :param artifact_template_id: The ID of the artifact template to use.
        :param task_scheduling: The scheduling configuration for the task.
        :return: A `Task` object containing the details of the created task.
        :rtype: Task
        """
        if not artifact_template_id or not artifact_template_id.strip():
            raise ValueError("Artifact Template ID must be provided.")
        if not task_scheduling:
            raise ValueError("Task Scheduling must be provided.")

        artifact_manager = self.artifact_manager
        task_manager = self.task_manager

        templates = artifact_manager.get_public_templates()
        template = None
        for v in templates:
            if v.template_id == artifact_template_id:
                template = v
        if not template:
            raise ValueError(f"Template with ID {artifact_template_id} not found.")
        if not template.template_data:
            raise ValueError("Template does not contain template data.")
        if not template.template_data.ray:
            raise ValueError("Template does not contain Ray configuration.")
        if not template.template_data.resources:
            raise ValueError("Template does not contain resource configuration.")

        artifact_id = artifact_manager.create_artifact_from_template(artifact_template_id)

        logger.info(f"Successfully created artifact from template, artifact_id: {artifact_id}")
        # Wait for the artifact to be ready
        while True:
            try:
                artifact = artifact_manager.get_artifact(artifact_id)
                logger.info(f"Successfully got artifact info, artifact status: {artifact.build_status}")
                # Wait until the artifact is ready
                if artifact.build_status == BuildStatus.SUCCESS:
                    break
            except Exception as e:
                raise e
            # Wait for 2 seconds
            time.sleep(2)
        try:
            # Create a task
            task = task_manager.create_task(Task(
                config=TaskConfig(
                    ray_task_config=RayTaskConfig(
                        ray_version=template.ray.version,
                        file_path=template.ray.file_path,
                        artifact_id=artifact_id,
                        deployment_name=template.ray.deployment_name,
                        replica_resource=ReplicaResource(
                            cpu=template.resources.cpu,
                            ram_gb=template.resources.memory,
                            gpu=template.resources.gpu,
                        ),
                    ),
                    task_scheduling=task_scheduling,
                ),
            ))

            logger.info(f"Successfully created task, task_id: {task.task_id}")
            # Start the task
            task_manager.start_task(task.task_id)
            logger.info(f"Successfully started task, task_id: {task.task_id}")
        except Exception as e:
            raise e

        return task

    @property
    def artifact_manager(self):
        """
        Lazy initialization for ArtifactManager.
        Ensures the Client instance controls its lifecycle.
        """
        if self._artifact_manager is None:
            self._artifact_manager = ArtifactManager(self.iam_client)
        return self._artifact_manager

    @property
    def task_manager(self):
        """
        Lazy initialization for TaskManager.
        Ensures the Client instance controls its lifecycle.
        """
        if self._task_manager is None:
            self._task_manager = TaskManager(self.iam_client)
        return self._task_manager

    @property
    def iam_manager(self):
        """
        Lazy initialization for IAMManager.
        Ensures the Client instance controls its lifecycle.
        """
        if self._iam_manager is None:
            self._iam_manager = IAMManager(self.iam_client)
        return self._iam_manager
