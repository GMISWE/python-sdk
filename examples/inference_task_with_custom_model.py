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
model_checkpoint_save_dir = f"files/model_garden/{model_name}"
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
serve_command = "vllm serve deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B --trust-remote-code --gpu-memory-utilization 0.8 --data-parallel-size 1 -tp 1 --enable-chunked-prefill --max_model_len 8192"
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

# Maybe Wait 10 minutes for the artifact to be ready
# time.sleep(10 * 60)


# Create Task based on Artifact
new_task_id = cli.task_manager.create_task_from_artifact_id(artifact_id, recommended_replica_resources, TaskScheduling(
    scheduling_oneoff=OneOffScheduling(
        trigger_timestamp=int(datetime.now().timestamp()),
        min_replicas=1,
        max_replicas=4,
    )
))

task = cli.task_manager.get_task(new_task_id)
print(f"Task created: {task.config.task_name}. You can check details at https://inference-engine.gmicloud.ai/user-console/task")

# Start Task and wait for it to be ready
cli.task_manager.start_task_and_wait(new_task_id)

# Call chat completion
api_key = "<YOUR_API_KEY>"
print(call_chat_completion(cli, api_key, new_task_id))

