# GMICloud SDK

## Overview
Before you start: Our service and GPU resource is currenly invite-only so please contact our team (getstarted@gmicloud.ai) to get invited if you don't have one yet.

The GMI Inference Engine SDK provides a Python interface for deploying and managing machine learning models in production environments. It allows users to create model artifacts, schedule tasks for serving models, and call inference APIs easily.

This SDK streamlines the process of utilizing GMI Cloud capabilities such as deploying models with Kubernetes-based Ray services, managing resources automatically, and accessing model inference endpoints. With minimal setup, developers can focus on building ML solutions instead of infrastructure.

## Features

- Artifact Management: Easily create, update, and manage ML model artifacts.
- Task Management: Quickly create, schedule, and manage deployment tasks for model inference.
- Usage Data Retrieval : Fetch and analyze usage data to optimize resource allocation.

## Installation

To install the SDK, use pip:

```bash
pip install gmicloud
```

## Setup

You must configure authentication credentials for accessing the GMI Cloud API. 
To create account and get log in info please visit **GMI inference platform: https://inference-engine.gmicloud.ai/**.

There are two ways to configure the SDK:

### Option 1: Using Environment Variables

Set the following environment variables:

```shell
export GMI_CLOUD_CLIENT_ID=<YOUR_CLIENT_ID> # Pick what every ID you need.
export GMI_CLOUD_EMAIL=<YOUR_EMAIL>
export GMI_CLOUD_PASSWORD=<YOUR_PASSWORD>
```

### Option 2: Passing Credentials as Parameters

Pass `client_id`, `email`, and `password` directly to the Client object when initializing it in your script:

```python
from gmicloud import Client

client = Client(client_id="<YOUR_CLIENT_ID>", email="<YOUR_EMAIL>", password="<YOUR_PASSWORD>")
```

## Quick Start

### 1. How to run the code in the example folder
```bash
cd path/to/gmicloud-sdk
# Create a virtual environment
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python -m examples.create_task_from_artifact_template.py
```

### 2. Example of create an inference task from an artifact template

This is the simplest example to deploy an inference task using an existing artifact template:

Up-to-date code in /examples/create_task_from_artifact_template.py

```python
from datetime import datetime
import os
import sys

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

# Testing with calling chat completion
print(call_chat_completion(cli, task.task_id))

```

### 3. Example of creating an inference task based on custom model with local vllm / SGLang serve command
* Full example is available at [examples/inference_task_with_custom_model.py](https://github.com/GMISWE/python-sdk/blob/main/examples/inference_task_with_custom_model.py)

1. Prepare custom model checkpoint (using a model downloaded from HF as an example)

```python
# Download model from huggingface
from huggingface_hub import snapshot_download

model_name = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
model_checkpoint_save_dir = "files/model_garden"
snapshot_download(repo_id=model_name, local_dir=model_checkpoint_save_dir)
```

#### Pre-downloaded models
```
"deepseek-ai/DeepSeek-R1"
"deepseek-ai/DeepSeek-V3-0324"
"deepseek-ai/DeepSeek-R1-Distill-Llama-70B"
"deepseek-ai/DeepSeek-R1-Distill-Llama-8B"
"deepseek-ai/DeepSeek-R1-Distill-Qwen-14B"
"deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
"deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
"meta-llama/Llama-3.3-70B-Instruct"
"meta-llama/Llama-4-Maverick-17B-128E-Instruct"
"meta-llama/Llama-4-Scout-17B-16E-Instruct"
"Qwen/QwQ-32B"
```

2. Find a template of specific vllm or SGLang version

```python
# export GMI_CLOUD_CLIENT_ID=<YOUR_CLIENT_ID>
# export GMI_CLOUD_EMAIL=<YOUR_EMAIL>
# export GMI_CLOUD_PASSWORD=<YOUR_PASSWORD>
cli = Client()

# List templates offered by GMI cloud 
templates = cli.artifact_manager.list_public_template_names()
print(f"Found {len(templates)} templates: {templates}")
```

3. Pick a template (e.g. SGLang 0.4.5) and prepare a local serve command

```python
# Example for vllm server
picked_template_name = "gmi_vllm_0.8.4"
serve_command = "vllm serve deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B --trust-remote-code --gpu-memory-utilization 0.8"

# Example for sglang server
picked_template_name = "gmi_sglang_0.4.5.post1"
serve_command = "python3 -m sglang.launch_server --model-path deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B --trust-remote-code --mem-fraction-static 0.8 --tp 2"
```

4. Create an artifact. you can pass `pre_download_model` parameter. If you want custom model, upload model checkpoint to the artifactThe artifact can be reused to create inference tasks later. Artifact also suggests recommended resources for each inference server replica

```python
artifact_name = "artifact_hello_world"
artifact_id, recommended_replica_resources = cli.artifact_manager.create_artifact_for_serve_command_and_custom_model(
    template_name=picked_template_name,
    artifact_name=artifact_name,
    serve_command=serve_command,
    gpu_type="H100",
    artifact_description="This is a test artifact",
    pre_download_model=pick_pre_downloaded_model,
)
print(f"Created artifact {artifact_id} with recommended resources: {recommended_replica_resources}")
```

Alternatively, Upload a custom model checkpoint to artifact
```python
cli.artifact_manager.upload_model_files_to_artifact(artifact_id, model_checkpoint_save_dir)

# Maybe Wait 10 minutes for the artifact to be ready
time.sleep(10 * 60)
```

5. Create Inference task (defining min/max inference replica), start and wait

```python
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
```

6. Test with sample chat completion request with OpenAI client

```python
pi_key = "<YOUR_API_KEY>"
endpoint_url = cli.task_manager.get_task_endpoint_url(new_task_id)
open_ai = OpenAI(
    base_url=os.getenv("OPENAI_API_BASE", f"https://{endpoint_url}/serve/v1/"),
    api_key=api_key
)
# Make a chat completion request using the new OpenAI client.
completion = open_ai.chat.completions.create(
    model=picked_template_name,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who are you?"},
    ],
    max_tokens=500,
    temperature=0.7
)
print(completion.choices[0].message.content)
```


## API Reference

### Client

Represents the entry point to interact with GMI Cloud APIs.
Client(
client_id: Optional[str] = "",
email: Optional[str] = "",
password: Optional[str] = ""
)

### Artifact Management

* get_artifact_templates(): Fetch a list of available artifact templates.
* create_artifact_from_template(template_id: str): Create a model artifact from a given template.
* get_artifact(artifact_id: str): Get details of a specific artifact.

### Task Management

* create_task_from_artifact_template(template_id: str, scheduling: TaskScheduling): Create and schedule a task using an
  artifact template.
* start_task(task_id: str): Start a task.
* get_task(task_id: str): Retrieve the status and details of a specific task.

## Notes & Troubleshooting
