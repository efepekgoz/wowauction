import psycopg2
from backend.config import DB_URI

def insert_auctions(auction_list):
    """
    Inserts a list of auction dictionaries into the PostgreSQL 'auctions' table.
    Each dict must contain: item_id, quantity, buyout, time_left, last_seen
    """
    conn = psycopg2.connect(DB_URI)
    cur = conn.cursor()

    query = """
    INSERT INTO auctions (item_id, quantity, buyout, time_left, last_seen)
    VALUES (%s, %s, %s, %s, %s)
    """

    try:
        for auction in auction_list:
            cur.execute(query, (
                auction["item_id"],
                auction["quantity"],
                auction["buyout"],
                auction["time_left"],
                auction["last_seen"]
            ))
        conn.commit()
        print(f"Inserted {len(auction_list)} rows into the database.")
    except Exception as e:
        conn.rollback()
        print("Error inserting data:", e)
    finally:
        cur.close()
        conn.close()
