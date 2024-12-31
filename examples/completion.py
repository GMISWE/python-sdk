import os
import time

from gmicloud import *

from openai import OpenAI


def call_chat_completion(client: Client, task_id: str) -> str:
    task_manager = client.task_manager
    endpoint_url = ""
    # Wait for the task to be ready
    while True:
        try:
            task = task_manager.get_task(task_id)
            print(f"task status: {task.task_status}")
            # Wait until the task is running
            if task.task_status != "running":
                continue
            print(task.endpoint_info.endpoint_status)
            if task.endpoint_info.endpoint_status == TaskEndpointStatus.RUNNING:
                endpoint_url = task.endpoint_info.endpoint_url
                break
            for endpoint in task.cluster_endpoints:
                if endpoint.endpoint_status == TaskEndpointStatus.RUNNING:
                    endpoint_url = endpoint.endpoint_url
                    break
            if endpoint_url:
                break
        except Exception as e:
            raise e
        # Wait for 10 seconds
        time.sleep(10)

    open_ai = OpenAI(
        base_url=os.getenv("OPENAI_API_BASE", f"http://{endpoint_url}/serve/v1/")
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

    print(completion)

    return completion.choices[0].message.content
