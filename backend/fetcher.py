import sys
import os

# Allow importing backend modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.to_database import insert_auctions

# Import the existing fetch functions
from backend.fetch_auctions import fetch_auction_data
from backend.process_data import process_auction_data
from backend.fetch_commodities import fetch_commodities

def fetch_all_auctions():
    """Fetch both regular auctions and commodities."""
    print("=== Starting complete auction data fetch ===")
    
    try:
        # Fetch regular auctions using existing script
        print("Fetching regular auctions...")
        raw_regular_data = fetch_auction_data()
        regular_auctions = process_auction_data(raw_regular_data)
        print(f"Processed {len(regular_auctions)} regular auctions")
        
        # Fetch commodity auctions using existing script
        print("Fetching commodity auctions...")
        # We need to modify the commodities script to return data instead of inserting
        commodity_auctions = fetch_commodities(return_data=True)
        print(f"Processed {len(commodity_auctions)} commodity auctions")
        
        # Combine all auctions
        all_auctions = regular_auctions + commodity_auctions
        
        print(f"\n=== Summary ===")
        print(f"Regular auctions: {len(regular_auctions)}")
        print(f"Commodity auctions: {len(commodity_auctions)}")
        print(f"Total auctions: {len(all_auctions)}")
        
        if all_auctions:
            # Insert all auctions into database (this will archive old data first)
            insert_auctions(all_auctions)
            print("✅ All auction data successfully updated!")
        else:
            print("❌ No auction data found to insert")
            
    except Exception as e:
        print(f"❌ Error during auction fetch: {e}")
        raise

if __name__ == "__main__":
    fetch_all_auctions() 