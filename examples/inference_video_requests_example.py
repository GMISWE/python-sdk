import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gmicloud import *
from gmicloud._internal._models import SubmitRequestRequest

#   ------ 1. login to the client ------
cli = Client()

#   ------ 2. get models ------
# models = cli.video_manager.get_models()
# print("[+]Available video models:\n",models,end="\n\n")

#   ------ 3. get model detail ------
# model_id = models[0].model
# model = cli.video_manager.get_model_detail(model_id)
# # print(f"[+]Model detail for {model_id}:\n", model,end="\n\n")

#   ------ 4. get requests ------
# res = cli.video_manager.get_requests(model_id)
# # print(f"[+]Request list for model {model_id}:\n", res,end="\n\n")
# request_id = res[0].request_id if res else None

#   ------ 5. get request detail ------
# detail = cli.video_manager.get_request_detail(request_id)
# # print(f"[+]Request detail for {request_id}:\n", detail, end="\n\n")


#  ------ 6. submit a new request ------

# request = SubmitRequestRequest(
#     # model=model_id,
#     # payload={
#     #     'image' : "https://images.fineartamerica.com/images/artworkimages/mediumlarge/2/sunshine-flowers-sharon-lapkin.jpg",
#     #     'cfg_scale' : 0.5,
#     #     'duration': '5',
#     #     'negative_prompt': '',
#     #     'prompt': 'flowers with sunshine'
#     # }
# )

request = SubmitRequestRequest(
    model = "Kling-Image2Video-V1.6-Pro",
    payload = {
        'image' : "https://images.fineartamerica.com/images/artworkimages/mediumlarge/2/sunshine-flowers-sharon-lapkin.jpg",
        'cfg_scale' : 0.5,
        "prompt": "flowers with sunshine",
        'duration': '5',
        "video_length": 5
    }
)
response = cli.video_manager.create_request(request)
print("[+]response submitted:\n", response, end="\n\n")
request_id = response.request_id

# #  ------ 7. loop to get request detail ------
def time_to_str(time_in_seconds):
    """Convert seconds to a human-readable format."""
    hours, remainder = divmod(time_in_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours)}:{int(minutes)}:{int(seconds)}"

count = 0
while True:
    response = cli.video_manager.get_request_detail(request_id)
    if isinstance(response, dict):
        print(f"[!]Error retrieving request detail: {response}")
        break
    time_str = time_to_str(time.time() - response.queued_at) if response.queued_at else "0:0:0"
    # time_str = time_to_str(count * 5)
    print(f"[+][{time_str}][+]Request detail for {request_id}:\n", response, end="\n\n")
    print(f"[+][{time_str}][+]Request status: {response.status}",end="\n\n")
    if response.status == "success":
        print("[+]Request completed successfully.")
        break
    elif response.status == "failed":
        print("[+]Request failed.")
        print("[+]Error message:", response.outcome if response.outcome else "No error message provided.")
        break
    elif response.status == "cancelled":
        print("[+]Request was cancelled.")
        break

    time.sleep(5)
    count += 1

