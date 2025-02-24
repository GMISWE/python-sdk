# GMICloud SDK (Beta)

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

You must configure authentication credentials for accessing the GMI Cloud API. There are two ways to configure the SDK:

### Option 1: Using Environment Variables

Set the following environment variables:

```shell
export GMI_CLOUD_CLIENT_ID=<YOUR_CLIENT_ID>
export GMI_CLOUD_EMAIL=<YOUR_EMAIL>
export GMI_CLOUD_PASSWORD=<YOUR_PASSWORD>
export GMI_CLOUD_API_KEY=<YOUR_API_KEY>
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

### 2. Create a Task from an Artifact Template

This is the simplest example to deploy an existing artifact template:

```python
from datetime import datetime
from gmicloud import Client, TaskScheduling, OneOffScheduling
from examples.completion import call_chat_completion

# Initialize the client
client = Client()

# Schedule and start a task from an artifact template
task = client.create_task_from_artifact_template(
    "qwen_2.5_14b_instruct_template_001",
    TaskScheduling(
        scheduling_oneoff=OneOffScheduling(
            trigger_timestamp=int(datetime.now().timestamp()) + 10,  # Delay by 10 seconds
            min_replicas=1,
            max_replicas=10,
        )
    )
)

# Make a chat completion request via the task endpoint
response = call_chat_completion(client, task.task_id)
print(response)
```

### 3. Step-by-Step Example: Create Artifact, Task, and Query the Endpoint

#### (a) Create an Artifact from a Template

First, you’ll retrieve all templates and create an artifact based on the desired template (e.g., "Llama3.1 8B"):

```python
from gmicloud import *


def create_artifact_from_template(client: Client) -> str:
    artifact_manager = client.artifact_manager

    # Get all artifact templates
    templates = artifact_manager.get_public_templates()
    for template in templates:
        if template.artifact_template_id == "qwen_2.5_14b_instruct_template_001":
            # Create an artifact from a template
            artifact_id = artifact_manager.create_artifact_from_template(
                artifact_template_id=template.artifact_template_id,
            )

            return artifact_id

    return ""
```

#### (b) Create a Task from the Artifact

Wait until the artifact becomes "ready" and then deploy it using task scheduling:

```python
from gmicloud import *
import time
from datetime import datetime

def create_task_and_start(client: Client, artifact_id: str) -> str:
    artifact_manager = client.artifact_manager
    # Wait for the artifact to be ready
    while True:
        try:
            artifact = artifact_manager.get_artifact(artifact_id)
            print(f"Artifact status: {artifact.build_status}")
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

        # Start the task
        task_manager.start_task(task.task_id)
    except Exception as e:
        raise e

    return task.task_id
```

### (c) Query the Model Endpoint

Once the task is running, use the endpoint for inference:

```python
from gmicloud import *
from examples.completion import call_chat_completion

# Initialize the Client
cli = Client()

# Create an artifact from a template
artifact_id = create_artifact_from_template(cli)

# Create a task and start it
task_id = create_task_and_start(cli, artifact_id)

# Call chat completion
print(call_chat_completion(cli, task_id))
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

* Ensure Credentials are Correct: Double-check your environment variables or parameters passed into the Client object.
* Artifact Status: It may take a few minutes for an artifact or task to transition to the "running" state.
* Inference Endpoint Readiness: Use the task endpoint only after the task status changes to "running".
* Default OpenAI Key: By default, the OpenAI API base URL is derived from the endpoint provided by GMI.

## Contributing

We welcome contributions to enhance the SDK. Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit changes with clear messages.
4. Submit a pull request for review.
