import os
import time
import logging

from typing import Optional

from ._internal._client._iam_client import IAMClient
from ._internal._manager._artifact_manager import ArtifactManager
from ._internal._manager._task_manager import TaskManager
from ._internal._manager._iam_manager import IAMManager
from ._internal._manager._video_manager import VideoManager
from ._internal._enums import BuildStatus, TaskStatus, TaskEndpointStatus
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
        self._video_manager = None

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
    def video_manager(self):
        """
        Lazy initialization for VideoManager.
        Ensures the Client instance controls its lifecycle.
        """
        if self._video_manager is None:
            self._video_manager = VideoManager(self.iam_client)
        return self._video_manager

    @property
    def iam_manager(self):
        """
        Lazy initialization for IAMManager.
        Ensures the Client instance controls its lifecycle.
        """
        if self._iam_manager is None:
            self._iam_manager = IAMManager(self.iam_client)
        return self._iam_manager

    # def list_templates(self) -> list[str]:
    #     """
    #     List all public templates.

    #     :return: A list of template names.
    #     :rtype: list[str]
    #     """
    #     template_names = []
    #     try: 
    #         templates = self.artifact_manager.get_public_templates()
    #         for template in templates:
    #             if template.template_data and template.template_data.name:
    #                 template_names.append(template.template_data.name)
    #         return template_names
    #     except Exception as e:
    #         logger.error(f"Failed to get artifact templates, Error: {e}")
    #         return []
        
    # def wait_for_artifact_ready(self, artifact_id: str, timeout_s: int = 900) -> None:
    #     """
    #     Wait for an artifact to be ready.

    #     :param artifact_id: The ID of the artifact to wait for.
    #     :param timeout_s: The timeout in seconds.
    #     :return: None
    #     """
    #     artifact_manager = self.artifact_manager
    #     start_time = time.time()
    #     while True:
    #         try:
    #             artifact = artifact_manager.get_artifact(artifact_id)
    #             if artifact.build_status == BuildStatus.SUCCESS:
    #                 return
    #             elif artifact.build_status in [BuildStatus.FAILED, BuildStatus.TIMEOUT, BuildStatus.CANCELLED]:
    #                 raise Exception(f"Artifact build failed, status: {artifact.build_status}")
    #         except Exception as e:
    #             logger.error(f"Failed to get artifact, Error: {e}")
    #         if time.time() - start_time > timeout_s:
    #             raise Exception(f"Artifact build takes more than {timeout_s // 60} minutes. Testing aborted.")
    #         time.sleep(10)
        
    # def create_artifact_from_template(self, artifact_template_name: str) -> tuple[str, ReplicaResource]:
    #     """
    #     Create an artifact from a template.

    #     :param artifact_template_name: The name of the template to use.
    #     :return: A tuple containing the artifact ID and the recommended replica resources.
    #     :rtype: tuple[str, ReplicaResource]
    #     """
    #     artifact_manager = self.artifact_manager

    #     recommended_replica_resources = None
    #     template_id = None
    #     try:
    #         templates = artifact_manager.get_public_templates()
    #     except Exception as e:
    #         logger.error(f"Failed to get artifact templates, Error: {e}")
    #     for template in templates:
    #         if template.template_data and template.template_data.name == artifact_template_name:
    #             resources_template = template.template_data.resources
    #             recommended_replica_resources = ReplicaResource(
    #                 cpu=resources_template.cpu,
    #                 ram_gb=resources_template.memory,
    #                 gpu=resources_template.gpu,
    #                 gpu_name=resources_template.gpu_name,
    #             )
    #             template_id = template.template_id
    #             break
    #     if not template_id:
    #         raise ValueError(f"Template with name {artifact_template_name} not found.")
    #     try: 
    #         artifact_id = artifact_manager.create_artifact_from_template(template_id)
    #         self.wait_for_artifact_ready(artifact_id)
    #         return artifact_id, recommended_replica_resources
    #     except Exception as e:
    #         logger.error(f"Failed to create artifact from template, Error: {e}")
    #         raise e
        
    # def create_task(self, artifact_id: str, replica_resources: ReplicaResource, task_scheduling: TaskScheduling) -> str:
    #     """
    #     Create a task.

    #     :param artifact_id: The ID of the artifact to use.
    #     :param replica_resources: The recommended replica resources.
    #     :param task_scheduling: The scheduling configuration for the task.
    #     :return: The ID of the created task.
    #     :rtype: str
    #     """
    #     task_manager = self.task_manager
    #     task = None
    #     try:
    #         task = task_manager.create_task(Task(
    #             config=TaskConfig(
    #                 ray_task_config=RayTaskConfig(
    #                     artifact_id=artifact_id,
    #                     file_path="serve",
    #                     deployment_name="app",
    #                     replica_resource=replica_resources,
    #                 ),
    #                 task_scheduling = task_scheduling,
    #             ),
    #         ))
    #     except Exception as e:
    #         logger.error(f"Failed to create task, Error: {e}")
    #         raise e
    #     return task.task_id 
    
    # def start_task_and_wait(self, task_id: str, timeout_s: int = 900) -> Task:
    #     """
    #     Start a task and wait for it to be ready.

    #     :param task_id: The ID of the task to start.
    #     :param timeout_s: The timeout in seconds.
    #     :return: The task object.
    #     :rtype: Task
    #     """
    #     task_manager = self.task_manager
    #     # trigger start task
    #     try:
    #         task_manager.start_task(task_id)
    #         logger.info(f"Started task ID: {task_id}")
    #     except Exception as e:
    #         logger.error(f"Failed to start task, Error: {e}")
    #         raise e
        
    #     start_time = time.time()
    #     while True:
    #         try:
    #             task = task_manager.get_task(task_id)
    #             if task.task_status == TaskStatus.RUNNING:
    #                 return task
    #             elif task.task_status in [TaskStatus.NEEDSTOP, TaskStatus.ARCHIVED]:
    #                 raise Exception(f"Unexpected task status after starting: {task.task_status}")
    #             # Also check endpoint status. 
    #             elif task.task_status == TaskStatus.RUNNING:
    #                 if task.endpoint_info and task.endpoint_info.endpoint_status == TaskEndpointStatus.RUNNING:
    #                     return task
    #                 elif task.endpoint_info and task.endpoint_info.endpoint_status in [TaskEndpointStatus.UNKNOWN, TaskEndpointStatus.ARCHIVED]:
    #                     raise Exception(f"Unexpected endpoint status after starting: {task.endpoint_info.endpoint_status}")
    #                 else:
    #                     logger.info(f"Pending endpoint starting. endpoint status: {task.endpoint_info.endpoint_status}")
    #             else:
    #                 logger.info(f"Pending task starting. Task status: {task.task_status}")

    #         except Exception as e:
    #             logger.error(f"Failed to get task, Error: {e}")
    #         if time.time() - start_time > timeout_s:
    #             raise Exception(f"Task creation takes more than {timeout_s // 60} minutes. Testing aborted.")
    #         time.sleep(10)

    # def stop_task(self, task_id: str, timeout_s: int = 900):
    #     task_manager = self.task_manager
    #     try:
    #         self.task_manager.stop_task(task_id)
    #         logger.info(f"Stopping task ID: {task_id}")
    #     except Exception as e:
    #         logger.error(f"Failed to stop task, Error: {e}")
    #     task_manager = self.task_manager
    #     start_time = time.time()
    #     while True:
    #         try:
    #             task = task_manager.get_task(task_id)
    #             if task.task_status == TaskStatus.IDLE:
    #                 break
    #         except Exception as e:
    #             logger.error(f"Failed to get task, Error: {e}")
    #         if time.time() - start_time > timeout_s:
    #             raise Exception(f"Task stopping takes more than {timeout_s // 60} minutes. Testing aborted.")
    #         time.sleep(10)

    # def archive_task(self, task_id: str, timeout_s: int = 900):
    #     task_manager = self.task_manager
    #     try:
    #         self.task_manager.archive_task(task_id)
    #         logger.info(f"Archived task ID: {task_id}")
    #     except Exception as e:
    #         logger.error(f"Failed to archive task, Error: {e}")  
