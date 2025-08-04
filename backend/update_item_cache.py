import sys
import os
import psycopg2
import time
import logging

# Allow running as standalone script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.config import DB_URI
from backend.items import get_or_fetch_item_name

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def update_missing_items():
    """Update item cache for items that don't have names in the database."""
    conn = psycopg2.connect(DB_URI)
    cur = conn.cursor()

    # Get all item IDs from auctions that don't have names in the items table
    cur.execute("""
        SELECT DISTINCT a.item_id 
        FROM auctions a 
        LEFT JOIN items i ON a.item_id = i.item_id 
        WHERE i.item_id IS NULL
        ORDER BY a.item_id
    """)
    
    missing_item_ids = [row[0] for row in cur.fetchall()]
    conn.close()

    if not missing_item_ids:
        logger.info("No missing items found!")
        return

    logger.info(f"Found {len(missing_item_ids)} items missing from cache.")

    # Process items with error handling and retries
    for i, item_id in enumerate(missing_item_ids, 1):
        try:
            logger.info(f"Processing {i}/{len(missing_item_ids)}: Item ID {item_id}")
            name, icon = get_or_fetch_item_name(item_id)
            
            # Always show the result (like original script)
            if name != "Unknown Item":
                logger.info(f"  ✓ ID: {item_id:<7} Name: {name}")
            else:
                logger.warning(f"  ✗ ID: {item_id:<7} Name: {name}")
            
            # Add a small delay to avoid overwhelming the API
            time.sleep(0.1)
            
        except Exception as e:
            logger.error(f"Error processing item {item_id}: {e}")
            # Continue with next item instead of crashing
            continue
        
        # Log progress every 100 items
        if i % 100 == 0:
            logger.info(f"Progress: {i}/{len(missing_item_ids)} items processed")

def update_all_items():
    """Update item cache for all items in auctions table."""
    conn = psycopg2.connect(DB_URI)
    cur = conn.cursor()

    cur.execute("SELECT DISTINCT item_id FROM auctions ORDER BY item_id")
    item_ids = [row[0] for row in cur.fetchall()]
    conn.close()

    if not item_ids:
        logger.info("No items found in auctions table!")
        return

    logger.info(f"Found {len(item_ids)} unique items in auctions.")

    # Process items with error handling and retries
    for i, item_id in enumerate(item_ids, 1):
        try:
            logger.info(f"Processing {i}/{len(item_ids)}: Item ID {item_id}")
            name, icon = get_or_fetch_item_name(item_id)
            
            # Always show the result (like original script)
            if name != "Unknown Item":
                logger.info(f"  ✓ ID: {item_id:<7} Name: {name}")
            else:
                logger.warning(f"  ✗ ID: {item_id:<7} Name: {name}")
            
            # Add a small delay to avoid overwhelming the API
            time.sleep(0.1)
            
        except Exception as e:
            logger.error(f"Error processing item {item_id}: {e}")
            # Continue with next item instead of crashing
            continue
        
        # Log progress every 100 items
        if i % 100 == 0:
            logger.info(f"Progress: {i}/{len(item_ids)} items processed")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Update item cache')
    parser.add_argument('--missing-only', action='store_true', 
                       help='Only update items missing from cache')
    parser.add_argument('--all', action='store_true', 
                       help='Update all items (default)')
    
    args = parser.parse_args()
    
    if args.missing_only:
        update_missing_items()
    else:
        update_all_items() 