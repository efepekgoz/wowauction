import psycopg2
from datetime import datetime
from backend.config import DB_URI

def insert_auctions(auction_list):
    """
    Inserts a list of auction dictionaries into the PostgreSQL 'auctions' table.
    Each dict must contain: item_id, quantity, buyout, time_left, last_seen
    """
    conn = psycopg2.connect(DB_URI)
    cur = conn.cursor()

    # First, archive current auctions to history table
    archive_current_auctions(cur)
    
    # Clear current auctions table
    cur.execute("DELETE FROM auctions")
    
    # Insert new auctions
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
        print(f"Archived previous auctions to history table.")
    except Exception as e:
        conn.rollback()
        print("Error inserting data:", e)
    finally:
        cur.close()
        conn.close()

def archive_current_auctions(cur):
    """
    Archives current auctions to the history table before inserting new ones.
    """
    try:
        # Copy current auctions to history table
        cur.execute("""
            INSERT INTO auction_history (item_id, quantity, buyout, time_left, snapshot_time)
            SELECT item_id, quantity, buyout, time_left, last_seen
            FROM auctions
            WHERE last_seen > NOW() - INTERVAL '1 hour'
        """)
        archived_count = cur.rowcount
        print(f"Archived {archived_count} auctions to history table.")
    except Exception as e:
        print(f"Error archiving auctions: {e}")

def get_auction_history(item_id=None, hours=24):
    """
    Retrieves historical auction data for analytics.
    If item_id is provided, returns data for that specific item.
    Otherwise returns data for all items within the specified hours.
    """
    conn = psycopg2.connect(DB_URI)
    cur = conn.cursor()
    
    try:
        if item_id:
            cur.execute("""
                SELECT item_id, quantity, buyout, time_left, snapshot_time
                FROM auction_history
                WHERE item_id = %s AND snapshot_time > NOW() - INTERVAL '%s hours'
                ORDER BY snapshot_time DESC
            """, (item_id, hours))
        else:
            cur.execute("""
                SELECT item_id, quantity, buyout, time_left, snapshot_time
                FROM auction_history
                WHERE snapshot_time > NOW() - INTERVAL '%s hours'
                ORDER BY snapshot_time DESC
            """, (hours,))
        
        return cur.fetchall()
    except Exception as e:
        print(f"Error retrieving auction history: {e}")
        return []
    finally:
        cur.close()
        conn.close()
