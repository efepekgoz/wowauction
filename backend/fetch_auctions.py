import sys
import os
import requests

# Allow running as standalone script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.auth import get_access_token

BASE_URL = "https://eu.api.blizzard.com"
NAMESPACE = "dynamic-eu"
LOCALE = "en_US"
CONNECTED_REALM_ID = 3674  # Twisting Nether (EU)

def fetch_auction_data(realm_id=CONNECTED_REALM_ID):
    access_token = get_access_token()
    url = f"{BASE_URL}/data/wow/connected-realm/{realm_id}/auctions"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "namespace": NAMESPACE,
        "locale": LOCALE
    }

    print("Requesting:", url)
    response = requests.get(url, headers=headers, params=params)

    print("Full request URL:", response.url)
    print("Status code:", response.status_code)

    if response.status_code == 200:
        data = response.json()
        print("Fetched auctions:", len(data.get("auctions", [])))
        return data
    else:
        print("Error response:", response.text)
        raise Exception(f"Failed to fetch auction data: {response.status_code}")

if __name__ == "__main__":
    from backend.process_data import process_auction_data
    from backend.to_database import insert_auctions

    raw_data = fetch_auction_data()
    cleaned = process_auction_data(raw_data)

    print("Sample cleaned auction:", cleaned[0] if cleaned else "No entries")
    print("Total processed auctions:", len(cleaned))

    if cleaned:
        insert_auctions(cleaned)