import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import requests
from urllib.parse import quote
from backend.auth import get_access_token

def get_connected_realm_id(realm_name: str, region="eu"):
    token = get_access_token(region)
    encoded_name = quote(realm_name)
    url = f"https://{region}.api.blizzard.com/data/wow/search/connected-realm"
    params = {
        "namespace": f"dynamic-{region}",
        "realms.name.en_US": encoded_name,
        "access_token": token
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        if not results:
            print(f"No match found for realm: {realm_name}")
            return None
        connected_realm = results[0].get("data", {})
        return connected_realm.get("id")
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

if __name__ == "__main__":
    realm_id = get_connected_realm_id("Twisting Nether")
    print("Connected realm ID:", realm_id)
