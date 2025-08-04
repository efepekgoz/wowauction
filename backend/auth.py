# backend/auth.py

import requests
from backend.config import API_CLIENT_ID, API_SECRET

DEFAULT_REGION = "eu"

def get_access_token(region=DEFAULT_REGION):
    """
    Get an OAuth2 access token for the specified Blizzard API region.
    Default region is 'eu'.
    """
    url = f"https://{region}.battle.net/oauth/token"
    response = requests.post(
        url,
        data={"grant_type": "client_credentials"},
        auth=(API_CLIENT_ID, API_SECRET)
    )

    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Failed to get token: {response.status_code} {response.text}")
