import os
import time
import logging

from gmicloud import *

from openai import OpenAI

logger = logging.getLogger(__name__)


def call_chat_completion(client: Client, task_id: str) -> str:
    task_manager = client.task_manager
    endpoint_url = ""
    # Wait for the task to be ready
    while True:
        try:
            # Wait for 5 seconds
            time.sleep(5)
            task = task_manager.get_task(task_id)
            logger.info(f"Successfully got task info, task status: {task.task_status}")
            # Wait until the task is running
            if task.task_status != "running":
                continue
            logger.info(f"Endpoint info status: {task.endpoint_info.endpoint_status}")
            if task.endpoint_info.endpoint_status == TaskEndpointStatus.RUNNING:
                endpoint_url = task.endpoint_info.endpoint_url
                break
            for endpoint in task.cluster_endpoints:
                logger.info(f"Cluster endpoint info status: {endpoint.endpoint_status}")
                if endpoint.endpoint_status == TaskEndpointStatus.RUNNING:
                    endpoint_url = endpoint.endpoint_url
                    break
            if endpoint_url:
                break
        except Exception as e:
            raise e

    time.sleep(30)  # Wait for the endpoint to be truly ready

    iam_manager = client.iam_manager
    api_key = os.getenv("GMI_CLOUD_API_KEY")
    if not api_key:
        api_key = iam_manager.create_org_api_key("example_api_key")
    open_ai = OpenAI(
        base_url=os.getenv("OPENAI_API_BASE", f"http://{endpoint_url}/serve/v1/"),
        api_key=api_key
    )
    # Make a chat completion request using the new OpenAI client.
    completion = open_ai.chat.completions.create(
        model="Qwen/Qwen2.5-14B-Instruct",
        messages=[
            {"role": "system", "content": "You are an excellent writer."},
            {"role": "user",
             "content": "Write a movie script about a dystopian past where intelligent machines have evolved to fight against humanity. A younger human challenges the ways of the elders and transforms into a cyborg to fight the machines."},
        ],
        max_tokens=2000,
        temperature=0.7
    )
    logger.info("Successfully called chat completion")

    return completion.choices[0].message.content
