import psycopg2
import os
import shutil
from datetime import datetime, timedelta
from backend.config import DB_URI

# ============================================================================
# BACKUP FUNCTIONS
# ============================================================================

def create_backup():
    """
    Create a backup of the auction_history table before running cleanup operations.
    """
    conn = psycopg2.connect(DB_URI)
    cur = conn.cursor()
    
    try:
        # Create backup table name with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_table_name = f"auction_history_backup_{timestamp}"
        
        print(f"Creating backup table: {backup_table_name}")
        
        # Create backup table
        cur.execute(f"""
            CREATE TABLE {backup_table_name} AS 
            SELECT * FROM auction_history
        """)
        
        # Get backup statistics
        cur.execute(f"SELECT COUNT(*) FROM {backup_table_name}")
        backup_count = cur.fetchone()[0]
        
        conn.commit()
        
        print(f"✅ Backup created successfully:")
        print(f"  Backup table: {backup_table_name}")
        print(f"  Records backed up: {backup_count:,}")
        
        return backup_table_name
        
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        conn.rollback()
        return None
    finally:
        cur.close()
        conn.close()

def list_backups():
    """
    List all available backup tables.
    """
    conn = psycopg2.connect(DB_URI)
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT table_name, 
                   (SELECT COUNT(*) FROM information_schema.tables t2 WHERE t2.table_name = t1.table_name) as exists
            FROM information_schema.tables t1
            WHERE table_name LIKE 'auction_history_backup_%'
            ORDER BY table_name DESC
        """)
        
        backups = cur.fetchall()
        
        if not backups:
            print("No backup tables found.")
            return []
        
        print("Available backup tables:")
        for table_name, exists in backups:
            if exists:
                cur.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cur.fetchone()[0]
                print(f"  {table_name}: {count:,} records")
            else:
                print(f"  {table_name}: (table not found)")
        
        return [row[0] for row in backups if row[1]]
        
    except Exception as e:
        print(f"Error listing backups: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def restore_backup(backup_table_name):
    """
    Restore auction_history table from a backup.
    """
    conn = psycopg2.connect(DB_URI)
    cur = conn.cursor()
    
    try:
        # Check if backup table exists
        cur.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{backup_table_name}'")
        if cur.fetchone()[0] == 0:
            print(f"❌ Backup table '{backup_table_name}' not found!")
            return False
        
        # Count current records
        cur.execute("SELECT COUNT(*) FROM auction_history")
        current_count = cur.fetchone()[0]
        
        # Count backup records
        cur.execute(f"SELECT COUNT(*) FROM {backup_table_name}")
        backup_count = cur.fetchone()[0]
        
        print(f"Restoring from backup: {backup_table_name}")
        print(f"  Current records: {current_count:,}")
        print(f"  Backup records: {backup_count:,}")
        
        # Clear current table and restore from backup
        cur.execute("DELETE FROM auction_history")
        cur.execute(f"INSERT INTO auction_history SELECT * FROM {backup_table_name}")
        
        conn.commit()
        
        print(f"✅ Restore completed successfully!")
        print(f"  Restored {backup_count:,} records")
        
        return True
        
    except Exception as e:
        print(f"❌ Error restoring backup: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def delete_backup(backup_table_name):
    """
    Delete a backup table.
    """
    conn = psycopg2.connect(DB_URI)
    cur = conn.cursor()
    
    try:
        cur.execute(f"DROP TABLE IF EXISTS {backup_table_name}")
        conn.commit()
        print(f"✅ Backup table '{backup_table_name}' deleted successfully!")
        
    except Exception as e:
        print(f"❌ Error deleting backup: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

# ============================================================================
# CLEANUP FUNCTIONS
# ============================================================================

def remove_outliers(create_backup_first=True):
    """
    Remove obvious outlier data points with backup protection.
    Uses conservative thresholds to avoid losing legitimate data.
    """
    backup_table = None
    
    if create_backup_first:
        print("Creating backup before outlier removal...")
        backup_table = create_backup()
        if not backup_table:
            print("❌ Failed to create backup. Aborting cleanup.")
            return False
    
    conn = psycopg2.connect(DB_URI)
    cur = conn.cursor()
    
    try:
        # Count records before cleanup
        cur.execute("SELECT COUNT(*) FROM auction_history")
        before_count = cur.fetchone()[0]
        
        print(f"Starting outlier removal (records before: {before_count:,})")
        
        # Conservative outlier removal - only remove truly extreme outliers
        cur.execute("""
            DELETE FROM auction_history 
            WHERE buyout > 10000000000  -- More than 1,000,000 gold (extremely high)
            OR (item_id = 2589 AND buyout > 1000000)  -- Linen Cloth more than 100 gold (very high)
            OR (item_id = 2589 AND buyout < 50)  -- Linen Cloth less than 0.005 gold (extremely low)
            OR buyout < 1  -- Any item less than 0.0001 gold (impossible)
        """)
        
        deleted_count = cur.rowcount
        conn.commit()
        
        # Count records after cleanup
        cur.execute("SELECT COUNT(*) FROM auction_history")
        after_count = cur.fetchone()[0]
        
        print(f"✅ Outlier removal completed:")
        print(f"  Records before: {before_count:,}")
        print(f"  Records deleted: {deleted_count:,}")
        print(f"  Records after: {after_count:,}")
        print(f"  Reduction: {((deleted_count) / before_count * 100):.2f}%")
        
        if backup_table:
            print(f"  Backup available: {backup_table}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during outlier removal: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def cleanup_daily_data(create_backup_first=True):
    """
    Keep only one data point per day per item with backup protection.
    Keeps the data point with the lowest price for each day.
    """
    backup_table = None
    
    if create_backup_first:
        print("Creating backup before daily cleanup...")
        backup_table = create_backup()
        if not backup_table:
            print("❌ Failed to create backup. Aborting cleanup.")
            return False
    
    conn = psycopg2.connect(DB_URI)
    cur = conn.cursor()
    
    try:
        # Count records before cleanup
        cur.execute("SELECT COUNT(*) FROM auction_history")
        before_count = cur.fetchone()[0]
        
        print(f"Starting daily cleanup (records before: {before_count:,})")
        
        # Keep the data point with the lowest price for each day per item
        cur.execute("""
            DELETE FROM auction_history 
            WHERE id NOT IN (
                SELECT DISTINCT ON (item_id, DATE(snapshot_time)) id
                FROM auction_history 
                ORDER BY item_id, DATE(snapshot_time), buyout ASC
            )
        """)
        
        deleted_count = cur.rowcount
        conn.commit()
        
        # Count records after cleanup
        cur.execute("SELECT COUNT(*) FROM auction_history")
        after_count = cur.fetchone()[0]
        
        print(f"✅ Daily cleanup completed:")
        print(f"  Records before: {before_count:,}")
        print(f"  Records deleted: {deleted_count:,}")
        print(f"  Records after: {after_count:,}")
        print(f"  Reduction: {((deleted_count) / before_count * 100):.1f}%")
        
        if backup_table:
            print(f"  Backup available: {backup_table}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during daily cleanup: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def cleanup_old_data(days_to_keep=30, create_backup_first=True):
    """
    Remove historical data older than specified days with backup protection.
    """
    backup_table = None
    
    if create_backup_first:
        print("Creating backup before old data cleanup...")
        backup_table = create_backup()
        if not backup_table:
            print("❌ Failed to create backup. Aborting cleanup.")
            return False
    
    conn = psycopg2.connect(DB_URI)
    cur = conn.cursor()
    
    try:
        # Count records before cleanup
        cur.execute("SELECT COUNT(*) FROM auction_history")
        before_count = cur.fetchone()[0]
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        print(f"Starting old data cleanup (records before: {before_count:,})")
        print(f"  Removing data older than: {cutoff_date.strftime('%Y-%m-%d')}")
        
        # Delete old records
        cur.execute("""
            DELETE FROM auction_history 
            WHERE snapshot_time < %s
        """, (cutoff_date,))
        
        deleted_count = cur.rowcount
        conn.commit()
        
        # Count records after cleanup
        cur.execute("SELECT COUNT(*) FROM auction_history")
        after_count = cur.fetchone()[0]
        
        print(f"✅ Old data cleanup completed:")
        print(f"  Records before: {before_count:,}")
        print(f"  Records deleted: {deleted_count:,}")
        print(f"  Records after: {after_count:,}")
        print(f"  Kept data from: {cutoff_date.strftime('%Y-%m-%d')} onwards")
        
        if backup_table:
            print(f"  Backup available: {backup_table}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during old data cleanup: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def get_stats():
    """
    Get statistics about the auction_history table.
    """
    conn = psycopg2.connect(DB_URI)
    cur = conn.cursor()
    
    try:
        # Total records
        cur.execute("SELECT COUNT(*) FROM auction_history")
        total_records = cur.fetchone()[0]
        
        # Table size
        cur.execute("SELECT pg_size_pretty(pg_total_relation_size('auction_history'))")
        table_size = cur.fetchone()[0]
        
        # Date range
        cur.execute("SELECT MIN(snapshot_time), MAX(snapshot_time) FROM auction_history")
        min_date, max_date = cur.fetchone()
        
        # Records per day (average)
        cur.execute("""
            SELECT COUNT(*) / GREATEST(EXTRACT(EPOCH FROM (MAX(snapshot_time) - MIN(snapshot_time))) / 86400, 1) as avg_per_day
            FROM auction_history
        """)
        avg_per_day = cur.fetchone()[0]
        
        print(f"History Table Statistics:")
        print(f"  Total records: {total_records:,}")
        print(f"  Table size: {table_size}")
        print(f"  Date range: {min_date} to {max_date}")
        print(f"  Average records per day: {avg_per_day:,.0f}")
        
    except Exception as e:
        print(f"Error getting stats: {e}")
    finally:
        cur.close()
        conn.close()

def preview_cleanup_impact():
    """
    Preview what would be deleted without actually deleting anything.
    """
    conn = psycopg2.connect(DB_URI)
    cur = conn.cursor()
    
    try:
        print("=== PREVIEW: Outlier Analysis ===")
        
        # Check for extreme outliers
        cur.execute("""
            SELECT COUNT(*) FROM auction_history 
            WHERE buyout > 10000000000
        """)
        extreme_high = cur.fetchone()[0]
        
        cur.execute("""
            SELECT COUNT(*) FROM auction_history 
            WHERE buyout < 1
        """)
        extreme_low = cur.fetchone()[0]
        
        cur.execute("""
            SELECT COUNT(*) FROM auction_history 
            WHERE item_id = 2589 AND buyout > 1000000
        """)
        linen_high = cur.fetchone()[0]
        
        cur.execute("""
            SELECT COUNT(*) FROM auction_history 
            WHERE item_id = 2589 AND buyout < 50
        """)
        linen_low = cur.fetchone()[0]
        
        print(f"  Extreme high prices (>1M gold): {extreme_high:,}")
        print(f"  Extreme low prices (<0.0001g): {extreme_low:,}")
        print(f"  Linen Cloth high prices (>100g): {linen_high:,}")
        print(f"  Linen Cloth low prices (<0.005g): {linen_low:,}")
        
        total_outliers = extreme_high + extreme_low + linen_high + linen_low
        print(f"  Total outliers to remove: {total_outliers:,}")
        
        print("\n=== PREVIEW: Daily Data Analysis ===")
        
        # Count total records
        cur.execute("SELECT COUNT(*) FROM auction_history")
        total_records = cur.fetchone()[0]
        
        # Count unique item-date combinations
        cur.execute("""
            SELECT COUNT(DISTINCT (item_id, DATE(snapshot_time))) 
            FROM auction_history
        """)
        unique_combinations = cur.fetchone()[0]
        
        print(f"  Total records: {total_records:,}")
        print(f"  Unique item-date combinations: {unique_combinations:,}")
        print(f"  Records to keep (lowest price per day per item): {unique_combinations:,}")
        print(f"  Records to remove: {total_records - unique_combinations:,}")
        
    except Exception as e:
        print(f"Error during preview: {e}")
    finally:
        cur.close()
        conn.close()

# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        # Backup commands
        if command == "backup":
            create_backup()
        elif command == "backups":
            list_backups()
        elif command == "restore" and len(sys.argv) > 2:
            restore_backup(sys.argv[2])
        elif command == "delete-backup" and len(sys.argv) > 2:
            delete_backup(sys.argv[2])
        
        # Cleanup commands
        elif command == "outliers":
            remove_outliers()
        elif command == "daily":
            cleanup_daily_data()
        elif command == "old" and len(sys.argv) > 2:
            days = int(sys.argv[2])
            cleanup_old_data(days)
        elif command == "preview":
            preview_cleanup_impact()
        elif command == "stats":
            get_stats()
        elif command == "all":
            print("Running all cleanup operations with backups...")
            if remove_outliers():
                if cleanup_daily_data(create_backup_first=False):
                    cleanup_old_data(30, create_backup_first=False)
        else:
            print("Usage: python cleanup.py [command]")
            print("\nBackup commands:")
            print("  backup                    - Create a backup")
            print("  backups                   - List all backups")
            print("  restore <table_name>      - Restore from backup")
            print("  delete-backup <table_name> - Delete a backup")
            print("\nCleanup commands:")
            print("  outliers                  - Remove extreme outliers (with backup)")
            print("  daily                     - Keep lowest price per day per item (with backup)")
            print("  old <days>                - Remove data older than X days (with backup)")
            print("  preview                   - Show what would be deleted without doing it")
            print("  stats                     - Show table statistics")
            print("  all                       - Run all cleanup operations")
    else:
        get_stats()
