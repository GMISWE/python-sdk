from datetime import datetime
import os
import sys

# To allow this script to be executed from other directories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gmicloud import *
from examples.completion import call_chat_completion

cli = Client()

# List templates offered by GMI cloud 
templates = cli.artifact_manager.list_public_template_names()
print(f"Found {len(templates)} templates: {templates}")

# Pick a template from the list
pick_template = "Llama-3.1-8B"

# Create Artifact from template
artifact_id, recommended_replica_resources = cli.artifact_manager.create_artifact_from_template_name(templates[0])
print(f"Created artifact {artifact_id} with recommended replica resources: {recommended_replica_resources}")

# Create Task based on Artifact
new_task = Task(
    config=TaskConfig(
        ray_task_config=RayTaskConfig(
            artifact_id=artifact_id,
            file_path="serve",
            deployment_name="app",
            replica_resource=recommended_replica_resources,
        ),
        task_scheduling = TaskScheduling(
            scheduling_oneoff=OneOffScheduling(
                trigger_timestamp=int(datetime.now().timestamp()),
                min_replicas=1,
                max_replicas=1,
            )
        ),
    ),
)
task = cli.task_manager.create_task(new_task)
task_id = task.task_id
task = cli.task_manager.get_task(task_id)
print(f"Task created: {task.config.task_name}. You can check details at https://inference-engine.gmicloud.ai/user-console/task")

# Start Task and wait for it to be ready
cli.task_manager.start_task_and_wait(task_id)

# Call chat completion
print(call_chat_completion(cli, task_id))
