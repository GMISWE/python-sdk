from datetime import datetime
import os
import sys

# To allow this script to be executed from other directories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gmicloud import *
from examples.completion import call_chat_completion

cli = Client()

# List templates offered by GMI cloud 
templates = cli.list_templates()
print(f"Found {len(templates)} templates: {templates}")

# Pick a template from the list
pick_template = "Llama-3.1-8B"

# Create Artifact from template
artifact_id, recommended_replica_resources = cli.create_artifact_from_template(templates[0])
print(f"Created artifact {artifact_id} with recommended replica resources: {recommended_replica_resources}")

# Create Task based on Artifact
task_id = cli.create_task(artifact_id, recommended_replica_resources, TaskScheduling(
    scheduling_oneoff=OneOffScheduling(
        trigger_timestamp=int(datetime.now().timestamp()),
        min_replicas=1,
        max_replicas=1,
    )
))
task = cli.task_manager.get_task(task_id)
print(f"Task created: {task.config.task_name}. You can check details at https://inference-engine.gmicloud.ai/user-console/task")

# Start Task and wait for it to be ready
cli.start_task_and_wait(task.task_id)

# Call chat completion
print(call_chat_completion(cli, task.task_id))
