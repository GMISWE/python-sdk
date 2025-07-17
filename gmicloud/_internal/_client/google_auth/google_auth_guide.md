## Set Up a Google Cloud Credentials
```
1. Go to the Google Cloud Console > https://console.cloud.google.com/

2. Navigate to Quick access > APIs & Services > Credentials.

3. Click "Create Credentials" → choose "OAuth client ID".

4. Select "Desktop application" (for CLI tools) and create.

5. Download the OAuth 2.0 client credentials (JSON file).

6. Rename the JSON file to `credentials.json`

7. Move it into the directory: `python-sdk/gmicloud/_internal/_client/google_auth/`
```


## Update the requirements.txt

- Add the google-auth-oauthlib library to the requirements.txt file
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```


## Usage Example
- Create an example Python file in the examples directory

``` python
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from gmicloud import *

email = "example@gmail.com"

cli = Client(email=email, login_type='google')
org_id = cli.iam_client.get_organization_id()
print(f"Organization ID: {org_id}")
```


- Command Line Output
- If this is your first time logging in with Google using this email:

```
Please visit the following URL to authorize:

auth url : 
https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=147690667088-72mtekoc82tkfvp391o11ojiaj5unc8d.apps.googleusercontent.com&redirect_uri=urn%3Aietf%3Awg%3Aoauth%3A2.0%3Aoob&scope=openid+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.profile&state=28MUAwJ3tskCcvKIzWSkUVWhGofcGW&prompt=consent&access_type=offline

After authorization, you will get an authorization code, please enter it below:

Please enter the authorization code: 
```

- Copy the auth URL to your browser
- Log in to your Google account
- Copy the authorization code into the command line
- Authentication succeed
- Check if it was written to config: `cat ~/.gmicloud.config.json`


## Possible Exceptions

```
1. Exception: Authentication failed. Please check that your authentication code is correct for the auth URL.
   Cause: The authorization code is not for this generated URL

2. ValueError: The authenticated Google email does not match the provided email.
   Cause: Check that your provided email matches your logged-in Google account
```