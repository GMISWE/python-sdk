import os
import time
import logging

from gmicloud import *

from openai import OpenAI

logger = logging.getLogger(__name__)


def call_chat_completion(client: Client, task_id: str) -> str:
    task_manager = client.task_manager
    endpoint_url = ""
    try:
        task = task_manager.get_task(task_id)
        logger.info(f"Successfully got task info, task status: {task.task_status}")
        endpoint_url = task.endpoint_info.endpoint_url
    except Exception as e:
        raise e
    if not endpoint_url:
        raise Exception("Endpoint URL not found")
    
    iam_manager = client.iam_manager
    api_key = ""
    keys = iam_manager.get_org_api_keys()
    if len(keys) == 0:
        logger.info("No API keys found. Creating a new one.")
        api_key = iam_manager.create_org_api_key("example_api_key")
    else:
        api_key = keys[0].partialKey

    open_ai = OpenAI(
        base_url=os.getenv("OPENAI_API_BASE", f"http://{endpoint_url}/v1/"),
        api_key=api_key
    )
    # Make a chat completion request using the new OpenAI client.
    completion = open_ai.chat.completions.create(
        model="default",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who are you?"},
        ],
        max_tokens=500,
        temperature=0.7
    )
    logger.info("Successfully called chat completion")

    return completion.choices[0].message.content
