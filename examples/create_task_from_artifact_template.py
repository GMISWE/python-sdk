from datetime import datetime
import os
import sys

# To allow this script to be executed from other directories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gmicloud import *
from examples.completion import call_chat_completion

cli = Client()

# Create and start a task from an artifact template
task = cli.create_task_from_artifact_template("b6a6429f-9e18-4f76-a258-a3ba3e78ed67", TaskScheduling(
    scheduling_oneoff=OneOffScheduling(
        trigger_timestamp=int(datetime.now().timestamp()) + 10,
        min_replicas=1,
        max_replicas=10,
    )
))

print(call_chat_completion(cli, task.task_id))
