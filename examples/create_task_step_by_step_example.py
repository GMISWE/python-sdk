import time
from datetime import datetime
import os
import sys
import logging

# To allow this script to be executed from other directories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gmicloud import *
from examples.completion import call_chat_completion

logger = logging.getLogger(__name__)


def create_artifact_from_template(client: Client) -> str:
    artifact_manager = client.artifact_manager

    # Get all artifact templates
    templates = artifact_manager.get_public_templates()
    for template in templates:
        if template.template_id == "qwen_2.5_14b_instruct_template_001":
            # Create an artifact from a template
            artifact_id = artifact_manager.create_artifact_from_template(
                artifact_template_id=template.template_id,
            )

            return artifact_id

    return ""


def create_task_and_start(client: Client, artifact_id: str) -> str:
    artifact_manager = client.artifact_manager
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
        task_manager = client.task_manager
        # Create a task
        task = task_manager.create_task(Task(
            config=TaskConfig(
                ray_task_config=RayTaskConfig(
                    ray_version="2.40.0-py310-gpu",
                    file_path="serve",
                    artifact_id=artifact_id,
                    deployment_name="app",
                    replica_resource=ReplicaResource(
                        cpu=10,
                        ram_gb=100,
                        gpu=1,
                    ),
                ),
                task_scheduling=TaskScheduling(
                    scheduling_oneoff=OneOffScheduling(
                        trigger_timestamp=int(datetime.now().timestamp()) + 10,
                        min_replicas=1,
                        max_replicas=10,
                    )
                ),
            ),
        ))

        logger.info(f"Successfully created task, task_id: {task.task_id}")
        # Start the task
        task_manager.start_task(task.task_id)
        logger.info(f"Successfully started task, task_id: {task.task_id}")
    except Exception as e:
        raise e

    return task.task_id


# Initialize the Client
cli = Client()

# Create an artifact from a template
artifact_id = create_artifact_from_template(cli)
logger.info(f"Successfully created artifact from template, artifact_id: {artifact_id}")

# Create a task and start it
task_id = create_task_and_start(cli, artifact_id)

# Call chat completion
print(call_chat_completion(cli, task_id))
