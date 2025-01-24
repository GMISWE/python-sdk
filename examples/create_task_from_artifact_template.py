from datetime import datetime

from gmicloud import *
from examples.completion import call_chat_completion

if __name__ == '__main__':
    cli = Client()

    # Create and start a task from an artifact template
    task = cli.create_task_from_artifact_template("qwen_2.5_14b_instruct_template_001", TaskScheduling(
        scheduling_oneoff=OneOffScheduling(
            trigger_timestamp=int(datetime.now().timestamp()) + 10,
            min_replicas=1,
            max_replicas=10,
        )
    ))

    print(call_chat_completion(cli, task.task_id))
