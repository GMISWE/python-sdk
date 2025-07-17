import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gmicloud import *

# email = "yang.zhang@57blocks.com"
# cli = Client(login_type='google', email=email)

email = "emma@57blocks.com"
password = "ycXM11!2013$"

cli = Client(email=email, password=password)
org_id = cli.iam_client.get_organization_id()
print(f"Organization ID: {org_id}")

# api_key = cli.iam_manager.create_org_api_key("example_api_key")
# print(api_key)

keys = cli.iam_manager.get_org_api_keys()
for key in keys:
    print(key)

cli.iam_client.refresh_token()
print("Token refreshed successfully.", cli.iam_client.get_refresh_token())
