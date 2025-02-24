from datetime import datetime
import os
import sys

# To allow this script to be executed from other directories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gmicloud import *

cli = Client()
iam_manager = cli.iam_manager

api_key = os.getenv("GMI_CLOUD_API_KEY")
if not api_key:
    api_key = iam_manager.create_org_api_key("example_api_key")
print(api_key)

keys = iam_manager.get_org_api_keys()
for key in keys:
    print(key)
