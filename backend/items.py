import requests
import psycopg2
from backend.auth import get_access_token
from backend.config import DB_URI

BASE_URL = "https://eu.api.blizzard.com"
NAMESPACE = "static-eu"
LOCALE = "en_US"

def get_or_fetch_item_name(item_id, region="eu"):
    """
    Returns (name, icon_url) for item_id.
    Uses local DB cache or Blizzard API if missing.
    """
    conn = psycopg2.connect(DB_URI)
    cur = conn.cursor()
    cur.execute("SELECT name, icon_url FROM items WHERE item_id = %s", (item_id,))
    result = cur.fetchone()

    if result:
        cur.close()
        conn.close()
        return result  # (name, icon_url)

    token = get_access_token(region)

    # 1. Fetch item name and media link
    item_url = f"{BASE_URL}/data/wow/item/{item_id}"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"namespace": NAMESPACE, "locale": LOCALE}

    item_resp = requests.get(item_url, headers=headers, params=params)
    if item_resp.status_code != 200:
        print(f"Failed to fetch item {item_id}")
        cur.close()
        conn.close()
        return ("Unknown Item", None)

    item_data = item_resp.json()
    name = item_data.get("name", "Unknown Item")

    # 2. Fetch icon
    media_url = item_data.get("media", {}).get("key", {}).get("href")
    icon_url = None
    if media_url:
        media_resp = requests.get(media_url, headers=headers)
        if media_resp.status_code == 200:
            media_data = media_resp.json()
            icon_url = next(
                (a["value"] for a in media_data.get("assets", []) if a["key"] == "icon"), None
            )

    # 3. Cache result
    try:
        cur.execute(
            "INSERT INTO items (item_id, name, icon_url) VALUES (%s, %s, %s)",
            (item_id, name, icon_url)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("DB insert error:", e)

    cur.close()
    conn.close()
    
    # Return the fetched data
    return (name, icon_url)