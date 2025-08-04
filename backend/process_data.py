from datetime import datetime

def process_auction_data(raw_data):
    """
    Extracts a simplified list of auction entries from the full API response.
    Each entry includes: item_id, quantity, buyout, time_left, last_seen.
    """

    auctions = raw_data.get("auctions", [])
    processed = []

    for auction in auctions:
        item_id = auction["item"]["id"]
        quantity = auction.get("quantity", 1)
        buyout = auction.get("buyout")  # May be None (bidding-only auctions)

        if buyout is None:
            continue  # Skip if no buyout price

        time_left = auction.get("time_left", "UNKNOWN")

        processed.append({
            "item_id": item_id,
            "quantity": quantity,
            "buyout": buyout,
            "time_left": time_left,
            "last_seen": datetime.utcnow()
        })

    return processed
