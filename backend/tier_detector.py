import psycopg2
from backend.config import DB_URI

def get_tiered_items():
    """
    Detect tiered items by finding consecutive item IDs with the same name.
    Returns a dictionary mapping item_id to tier information.
    """
    conn = psycopg2.connect(DB_URI)
    cur = conn.cursor()
    
    try:
        # Get all items ordered by name and item_id
        cur.execute("""
            SELECT item_id, name 
            FROM items 
            ORDER BY name, item_id
        """)
        
        items = cur.fetchall()
        tiered_items = {}
        
        i = 0
        while i < len(items):
            current_name = items[i][1]
            current_id = items[i][0]
            
            # Find all consecutive items with the same name
            tier_group = []
            j = i
            while j < len(items) and items[j][1] == current_name:
                tier_group.append(items[j][0])
                j += 1
            
            # If we have exactly 3 items with the same name and consecutive IDs, they're tiered
            if len(tier_group) == 3:
                # Check if IDs are consecutive (or very close)
                is_consecutive = True
                for k in range(1, len(tier_group)):
                    if tier_group[k] - tier_group[k-1] > 5:  # Allow small gaps
                        is_consecutive = False
                        break
                
                if is_consecutive:
                    # Assign tier numbers (1, 2, 3)
                    for tier_num, item_id in enumerate(tier_group, 1):
                        tiered_items[item_id] = {
                            'tier': tier_num,
                            'total_tiers': 3,
                            'name': current_name
                        }
            
            i = j  # Skip to the next group
        
        return tiered_items
        
    finally:
        cur.close()
        conn.close()

def get_item_tier_info(item_id):
    """
    Get tier information for a specific item.
    Returns None if the item is not tiered.
    """
    tiered_items = get_tiered_items()
    return tiered_items.get(item_id)

def get_tiered_items_cache():
    """
    Get tiered items and cache the result for better performance.
    This should be called once and the result cached.
    """
    return get_tiered_items()

# Cache the tiered items for better performance
_tiered_items_cache = None

def get_cached_tiered_items():
    """
    Get cached tiered items, initializing the cache if needed.
    """
    global _tiered_items_cache
    if _tiered_items_cache is None:
        _tiered_items_cache = get_tiered_items()
    return _tiered_items_cache

def get_cached_item_tier_info(item_id):
    """
    Get tier information for a specific item using the cache.
    """
    tiered_items = get_cached_tiered_items()
    return tiered_items.get(item_id)
