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

You must configure authentication credentials for accessing the GMI Cloud API. 
To create account and get log in info please visit **GMI inference platform: https://inference-engine.gmicloud.ai/**.

There are two ways to configure the SDK:

### Option 1: Using Environment Variables

Set the following environment variables:

```shell
export GMI_CLOUD_CLIENT_ID=<YOUR_CLIENT_ID>
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

### 2. Create an inference task from an artifact template

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
k