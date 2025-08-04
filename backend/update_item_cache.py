import sys
import os
import psycopg2

# Allow running as standalone script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.config import DB_URI
from backend.items import get_or_fetch_item_name

def update_all_missing_items():
    conn = psycopg2.connect(DB_URI)
    cur = conn.cursor()

    cur.execute("SELECT DISTINCT item_id FROM auctions")
    item_ids = [row[0] for row in cur.fetchall()]
    conn.close()

    print(f"Found {len(item_ids)} unique items in auctions.")

    for i, item_id in enumerate(item_ids, 1):
        name, icon = get_or_fetch_item_name(item_id)
        print(f"{i:5d}/{len(item_ids)}  ID: {item_id:<7}  Name: {name}")

if __name__ == "__main__":
    update_all_missing_items()
