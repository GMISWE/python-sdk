from datetime import datetime
import os
import sys
import time
# from huggingface_hub import snapshot_download  # Added to download model programmatically

# To allow this script to be executed from other directories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gmicloud import *
# from examples.completion import call_chat_completion
from openai import OpenAI


##### Pick a model to serve #####

# # Option 1: Prepare a model checkpoint to upload (e.g. download a non-popular from huggingface)
# from huggingface_hub import snapshot_download

# model_name = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
# model_checkpoint_save_dir = f"files/model_garden/{model_name}"
# snapshot_download(repo_id=model_name, local_dir=model_checkpoint_save_dir)

# Option 2: Use a pre-downloaded model checkpoint
# Check the full list of pre-downloaded models in README.md
pick_pre_downloaded_model = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"

os.environ["GMI_CLOUD_CLIENT_ID"] = "gmitest"
os.environ["GMI_CLOUD_EMAIL"] = "emma@57blocks.com"
os.environ["GMI_CLOUD_PASSWORD"] = "ycXM11!2013$"
# os.environ["GMI_CLOUD_API_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjcyNzY4NTQ1LTg2OTUtNGQ2NC04ODZlLThmZTUxN2YzODRlNSIsInR5cGUiOiJpZV9tb2RlbCJ9.Nslc9Sb4SawiXJvWavZm0YD80zaVlhVuzVo-rMxJ3lA"


##### Pick a serving template (vllm or SGLang) and prepare serve command #####

# Apply the following environment variables to your system first
# export GMI_CLOUD_CLIENT_ID=<YOUR_CLIENT_ID>
# export GMI_CLOUD_EMAIL=<YOUR_EMAIL>
# export GMI_CLOUD_PASSWORD=<YOUR_PASSWORD>
cli = Client()

# List templates offered by GMI cloud 
# templates = cli.artifact_manager.list_public_template_names()
# print(f"Found {len(templates)} templates: {templates}")

# Create an artifact from a template
# picked_template_name = "GMI_inference_template"

# Example for vllm serve command
picked_template_name = "gmi_vllm_0.8.4"
serve_command = "vllm serve deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B --trust-remote-code --gpu-memory-utilization 0.8 --data-parallel-size 1 -tp 2 --enable-chunked-prefill --max_model_len 8192"

# picked_template_name = "gmi_vllm_0.8.4"
# serve_command = "vllm serve deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B --trust-remote-code --tensor-parallel-size 1 --dtype half --gpu-memory-utilization 0.9 --max_model_len 4096"

# # Example for sglang serve command
picked_template_name = "gmi_sglang_0.4.5.post1"
# serve_command = "python3 -m sglang.launch_server --model-path deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B --trust-remote-code --tp-size 1 --mem-fraction-static 0.8"
serve_command = "python3 -m sglang.launch_server --model-path deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B --trust-remote-code --tp-size 2"

# # # ##### Create Artifact with template, model, serve command, and GPU type #####
artifact_name = "artifact_test_sglang"
artifact_id, recommended_replica_resources = cli.artifact_manager.create_artifact_for_serve_command_and_custom_model(
    template_name=picked_template_name,
    artifact_name=artifact_name,
    serve_command=serve_command,
    gpu_type="H100",
    artifact_description="This is a test artifact",
    pre_download_model=pick_pre_downloaded_model,
)
# print(f"Created artifact {artifact_id} with recommended resources: {recommended_replica_resources}")

# # # Alternatively, Upload a custom model checkpoint to artifact
# # # cli.artifact_manager.upload_model_files_to_artifact(artifact_id, model_checkpoint_save_dir)

# # # Maybe Wait 10 minutes for the artifact to be ready
# # # time.sleep(10 * 60)
# # # artifact_id = "5f415530-6823-4df9-8030-7036d338d82c"
# # recommended_replica_resources = ReplicaResource(cpu=16, ram_gb=60, gpu=1, gpu_name='H100')


# # ##### Create Task based on Artifact #####
# # Create Task based on Artifact
new_task_id = cli.task_manager.create_task_from_artifact_id(artifact_id, recommended_replica_resources, TaskScheduling(
    scheduling_oneoff=OneOffScheduling(
        trigger_timestamp=int(datetime.now().timestamp()),
        min_replicas=1,
        max_replicas=2,
    )
))
# print(f"-------------------------{new_task_id}---------------------------")
# task = cli.task_manager.get_task(new_task_id)
# # print(f"Task created: {task.config.task_name}. You can check details at https://inference-engine.gmicloud.ai/user-console/task")

# # # # Start Task and wait for it to be ready
# cli.task_manager.start_task_and_wait(new_task_id)


##### Testing the inference task #####
# Call chat completion
new_task_id = "0a3b0192-209b-4264-8a2b-368b6f58872b"
api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjQ3YjZjOTMxLWY2OWEtNDE3YS1iZjk5LWQ4ZmUxY2UwN2ZiOSIsInR5cGUiOiJpZV9tb2RlbCJ9.291t3S9tD2ba4ck9zOZaUUWy-SDqDMsG1DqSDDvJcVw"
# task = cli.task_manager.get_task(new_task_id)
# print({"task":task})
endpoint_url = cli.task_manager.get_task_endpoint_url(new_task_id)
# endpoint_url = "1bda90b61249.inference-engine-lccn11.gmi-dev-serving.com"
print(f"Endpoint URL: {endpoint_url}")

open_ai = OpenAI(
    base_url=os.getenv("OPENAI_API_BASE", f"https://{endpoint_url}/serve/v1/"),
    api_key=api_key
)
# Make a chat completion request using the new OpenAI client.
completion = open_ai.chat.completions.create(
    model="deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who are you?"},
    ],
    max_tokens=500,
    temperature=0.7
)
print(completion.choices[0].message.content)

# https://79bc3eca8d33.inference-engine-lccn11.gmi-dev-serving.com/serve
# "https://2e8b1bb96e61.inference-engine-lccn11.gmi-dev-serving.com/serve"

