from datetime import datetime
import os
import sys
import time
from huggingface_hub import snapshot_download  # Added to download model programmatically

# To allow this script to be executed from other directories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gmicloud import *
from examples.completion import call_chat_completion


# Download model from huggingface
from huggingface_hub import snapshot_download

# model_name = "AuriAetherwiing/MN-12B-Starcannon-v2"
model_name = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
model_checkpoint_save_dir = "files/model_garden"
snapshot_download(repo_id=model_name, local_dir=model_checkpoint_save_dir)


# Apply the following environment variables to your system first
# export GMI_CLOUD_CLIENT_ID=<YOUR_CLIENT_ID>
# export GMI_CLOUD_EMAIL=<YOUR_EMAIL>
# export GMI_CLOUD_PASSWORD=<YOUR_PASSWORD>
cli = Client()

# List templates offered by GMI cloud 
templates = cli.artifact_manager.list_public_template_names()
print(f"Found {len(templates)} templates: {templates}")

# Create an artifact from a template
# picked_template_name = "GMI_inference_template"

# Example for vllm server
picked_template_name = "gmi_vllm_0.8.4"
serve_command = "VLLM_USE_V1=1 vllm serve deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B --trust-remote-code --gpu-memory-utilization 0.8 -dp 2 -tp 2 --enable-chunked-prefill"

# Example for sglang server
# picked_template_name = "gmi_sglang_0.4.5.post1"
# serve_command = "python3 -m sglang.launch_server --model-path deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B --trust-remote-code --tp-size 2 --mem-fraction-static 0.8 --enable-torch-compile"

artifact_name = "artifact_hello_world"
artifact_id, recommended_replica_resources = cli.artifact_manager.create_artifact_for_serve_command_and_custom_model(
    template_name=picked_template_name,
    artifact_name=artifact_name,
    serve_command=serve_command,
    gpu_type="H100",
    artifact_description="This is a test artifact",
)
print(f"Created artifact {artifact_id} with recommended resources: {recommended_replica_resources}")

# Upload model files to artifact
cli.artifact_manager.upload_model_files_to_artifact(artifact_id, model_checkpoint_save_dir)

# Wait 10 minutes for the artifact to be ready
time.sleep(10 * 60)

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
                max_replicas=4,
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
