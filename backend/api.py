from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import psycopg2

from backend.config import DB_URI

app = FastAPI()

# Allow frontend to connect from anywhere (for now)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/items")
def get_all_items():
    conn = psycopg2.connect(DB_URI)
    cur = conn.cursor()
    cur.execute("SELECT item_id, name, icon_url FROM items ORDER BY name")
    items = [{"item_id": r[0], "name": r[1], "icon_url": r[2]} for r in cur.fetchall()]
    cur.close()
    conn.close()
    return items


from fastapi import Query
from datetime import datetime, timedelta

@app.get("/api/auctions")
def get_auctions(query: str = Query(None, description="Search query for item names")):
    conn = psycopg2.connect(DB_URI)
    cur = conn.cursor()
    
    if query:
        # Search by item name - group by item and aggregate
        cur.execute("""
            SELECT a.item_id, 
                   i.name, 
                   i.icon_url,
                   MIN(a.buyout) as lowest_price,
                   SUM(a.quantity) as total_quantity,
                   COUNT(*) as auction_count
            FROM auctions a
            JOIN items i ON a.item_id = i.item_id
            WHERE i.name ILIKE %s
            GROUP BY a.item_id, i.name, i.icon_url
            ORDER BY lowest_price ASC
        """, (f"%{query}%",))
    else:
        # Get all auctions - group by item and aggregate
        cur.execute("""
            SELECT a.item_id, 
                   i.name, 
                   i.icon_url,
                   MIN(a.buyout) as lowest_price,
                   SUM(a.quantity) as total_quantity,
                   COUNT(*) as auction_count
            FROM auctions a
            JOIN items i ON a.item_id = i.item_id
            GROUP BY a.item_id, i.name, i.icon_url
            ORDER BY lowest_price ASC
        """)
    
    results = []
    for row in cur.fetchall():
        item_id, name, icon_url, lowest_price, total_quantity, auction_count = row
        results.append({
            "item_id": item_id,
            "name": name,
            "icon_url": icon_url,
            "lowest_price": lowest_price,
            "total_quantity": total_quantity,
            "auction_count": auction_count
        })
    
    cur.close()
    conn.close()
    return results

@app.get("/api/auctions/history")
def get_auction_history(
    item_id: int = Query(None, description="Specific item ID to get history for"),
    hours: int = Query(24, description="Number of hours of history to retrieve")
):
    """Get historical auction data for analytics and trends."""
    conn = psycopg2.connect(DB_URI)
    cur = conn.cursor()
    
    try:
        if item_id:
            # Get history for specific item
            cur.execute("""
                SELECT ah.item_id, ah.quantity, ah.buyout, ah.time_left, ah.snapshot_time,
                       i.name, i.icon_url
                FROM auction_history ah
                JOIN items i ON ah.item_id = i.item_id
                WHERE ah.item_id = %s AND ah.snapshot_time > NOW() - INTERVAL '%s hours'
                ORDER BY ah.snapshot_time DESC
            """, (item_id, hours))
        else:
            # Get history for all items
            cur.execute("""
                SELECT ah.item_id, ah.quantity, ah.buyout, ah.time_left, ah.snapshot_time,
                       i.name, i.icon_url
                FROM auction_history ah
                JOIN items i ON ah.item_id = i.item_id
                WHERE ah.snapshot_time > NOW() - INTERVAL '%s hours'
                ORDER BY ah.snapshot_time DESC
            """, (hours,))
        
        results = []
        for row in cur.fetchall():
            item_id, quantity, buyout, time_left, snapshot_time, name, icon_url = row
            results.append({
                "item_id": item_id,
                "name": name,
                "icon_url": icon_url,
                "quantity": quantity,
                "buyout": buyout,
                "time_left": time_left,
                "snapshot_time": snapshot_time.isoformat() if snapshot_time else None
            })
        
        return results
    except Exception as e:
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()

@app.get("/api/auctions/trends")
def get_price_trends(
    item_id: int = Query(..., description="Item ID to get price trends for"),
    hours: int = Query(24, description="Number of hours to analyze")
):
    """Get price trends for a specific item over time."""
    conn = psycopg2.connect(DB_URI)
    cur = conn.cursor()
    
    try:
        # Get price trends grouped by hour
        cur.execute("""
            SELECT 
                DATE_TRUNC('hour', ah.snapshot_time) as hour,
                COUNT(*) as auction_count,
                AVG(ah.buyout) as avg_price,
                MIN(ah.buyout) as min_price,
                MAX(ah.buyout) as max_price,
                SUM(ah.quantity) as total_quantity
            FROM auction_history ah
            WHERE ah.item_id = %s AND ah.snapshot_time > NOW() - INTERVAL '%s hours'
            GROUP BY DATE_TRUNC('hour', ah.snapshot_time)
            ORDER BY hour DESC
        """, (item_id, hours))
        
        trends = []
        for row in cur.fetchall():
            hour, auction_count, avg_price, min_price, max_price, total_quantity = row
            trends.append({
                "hour": hour.isoformat() if hour else None,
                "auction_count": auction_count,
                "avg_price": float(avg_price) if avg_price else 0,
                "min_price": min_price,
                "max_price": max_price,
                "total_quantity": total_quantity
            })
        
        return trends
    except Exception as e:
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()

@app.get("/api/items/search")
def search_items(query: str = Query(..., description="Search query for item names")):
    """Quick search endpoint for dropdown suggestions - returns only names and icons."""
    if len(query) < 3:
        return []
    
    conn = psycopg2.connect(DB_URI)
    cur = conn.cursor()
    
    try:
        # First get items that start with the query (prefix matches)
        cur.execute("""
            SELECT item_id, name, icon_url, 1 as priority
            FROM items
            WHERE name ILIKE %s
            UNION ALL
            SELECT item_id, name, icon_url, 2 as priority
            FROM items
            WHERE name ILIKE %s AND name NOT ILIKE %s
            ORDER BY priority, name
            LIMIT 5
        """, (f"{query}%", f"%{query}%", f"{query}%"))
        
        results = []
        seen_items = set()
        
        for row in cur.fetchall():
            item_id, name, icon_url, priority = row
            if item_id not in seen_items:  # Avoid duplicates
                results.append({
                    "item_id": item_id,
                    "name": name,
                    "icon_url": icon_url
                })
                seen_items.add(item_id)
                if len(results) >= 5:  # Limit to 5 items
                    break
        
        return results
    finally:
        cur.close()
        conn.close()
