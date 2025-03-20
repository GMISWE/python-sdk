from datetime import datetime
import os
import sys
from huggingface_hub import snapshot_download  # Added to download model programmatically

# To allow this script to be executed from other directories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gmicloud import *
from examples.completion import call_chat_completion

cli = Client()

# Download model from huggingface
model_name = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
model_output_dir = "files/DeepSeek-R1-Distill-Qwen-1.5B"
snapshot_download(repo_id=model_name, local_dir=model_output_dir)

artifact_id = cli.artifact_manager.create_artifact_with_model_files(
    artifact_name="Example-DeepSeek-R1-Distill-Qwen-1.5B",
    artifact_file_path=f"{model_output_dir}.zip",
    model_directory=model_output_dir,
)

# Create Task based on Artifact
new_task = Task(
    config=TaskConfig(
        ray_task_config=RayTaskConfig(
            artifact_id=artifact_id,
            file_path="serve",
            deployment_name="app",
            replica_resource=ReplicaResource(
                cpu=3,
                ram_gb=32,
                gpu=2,
            ),
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
