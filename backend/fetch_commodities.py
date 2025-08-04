import sys
import os
import requests
from datetime import datetime, timezone

# Allow importing backend modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.auth import get_access_token
from backend.to_database import insert_auctions

BASE_URL = "https://eu.api.blizzard.com"
NAMESPACE = "dynamic-eu"
LOCALE = "en_US"

def fetch_commodities(return_data=False):
    """
    Fetch commodity auctions.
    
    Args:
        return_data (bool): If True, return processed data instead of inserting to database
    """
    token = get_access_token(region="eu")
    url = f"{BASE_URL}/data/wow/auctions/commodities"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    params = {
        "namespace": NAMESPACE,
        "locale": LOCALE
    }

    print("Requesting:", url)
    response = requests.get(url, headers=headers, params=params)

    print("Status code:", response.status_code)
    if response.status_code != 200:
        print("Error response:", response.text)
        raise Exception(f"Failed to fetch commodity data: {response.status_code}")

    data = response.json()
    auctions = data.get("auctions", [])

    print("Fetched commodity auctions:", len(auctions))

    # Process commodities data - note the different structure
    processed = []
    now = datetime.now(timezone.utc)  # Use timezone-aware datetime

    for auction in auctions:
        # Commodities use unit_price instead of buyout
        unit_price = auction.get("unit_price")
        if not unit_price:
            continue  # skip listings without unit price

        # Calculate total buyout price (unit_price * quantity)
        quantity = auction.get("quantity", 1)
        total_buyout = unit_price * quantity

        entry = {
            "item_id": auction["item"]["id"],
            "quantity": quantity,
            "buyout": total_buyout,  # Store total price in buyout field
            "time_left": auction.get("time_left", "UNKNOWN"),
            "last_seen": now
        }
        processed.append(entry)

    print("Processed commodity auctions:", len(processed))
    
    if return_data:
        return processed
    else:
        if processed:
            insert_auctions(processed)
        else:
            print("No valid commodity auctions found to insert")

if __name__ == "__main__":
    fetch_commodities()
