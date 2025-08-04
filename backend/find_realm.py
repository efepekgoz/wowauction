import sys
import os
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.auth import get_access_token

def get_connected_realm_id(slug: str, region="eu"):
    """Get connected realm ID by slug using the correct authentication method"""
    token = get_access_token(region)
    url = f"https://{region}.api.blizzard.com/data/wow/search/connected-realm"
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "namespace": f"dynamic-{region}",
        "realms.slug": slug,
        "locale": "en_US"
    }

    print(f"Searching for realm slug: {slug}")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Params: {params}")

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        if results:
            print(f"Found {len(results)} matching realms:")
            for i, result in enumerate(results):
                realm_data = result["data"]
                realms = realm_data.get("realms", [])
                if realms:
                    realm = realms[0]
                    name = realm.get("name", {}).get("en_US", "Unknown")
                    realm_slug = realm.get("slug", "Unknown")
                    print(f"  {i+1}. {name} (slug: {realm_slug}) - ID: {realm_data.get('id')}")
            return results[0]["data"].get("id")
        else:
            print(f"No match found for realm slug: {slug}")
            return None
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def search_realm_by_name(realm_name: str, region="eu"):
    """Search for a realm by name using the correct authentication method"""
    token = get_access_token(region)
    url = f"https://{region}.api.blizzard.com/data/wow/search/connected-realm"
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "namespace": f"dynamic-{region}",
        "realms.name.en_US": realm_name,
        "locale": "en_US"
    }

    print(f"Searching for realm containing: {realm_name}")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Params: {params}")

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        if results:
            print(f"Found {len(results)} matching realms:")
            for i, result in enumerate(results):
                realm_data = result["data"]
                realms = realm_data.get("realms", [])
                if realms:
                    realm = realms[0]
                    name = realm.get("name", {}).get("en_US", "Unknown")
                    realm_slug = realm.get("slug", "Unknown")
                    print(f"  {i+1}. {name} (slug: {realm_slug}) - ID: {realm_data.get('id')}")
            return results[0]["data"].get("id")
        else:
            print(f"No realms found containing: {realm_name}")
            return None
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def list_all_realms(region="eu", limit=20):
    """List all available realms using the correct authentication method"""
    token = get_access_token(region)
    url = f"https://{region}.api.blizzard.com/data/wow/connected-realm/index"
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "namespace": f"dynamic-{region}",
        "locale": "en_US"
    }

    print("Fetching all connected realms...")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Params: {params}")

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        connected_realms = data.get("connected_realms", [])
        print(f"Found {len(connected_realms)} connected realms")
        
        # Get details for first few realms
        for i, realm_url in enumerate(connected_realms[:limit]):
            realm_response = requests.get(realm_url, headers=headers)
            if realm_response.status_code == 200:
                realm_data = realm_response.json()
                realms = realm_data.get("realms", [])
                if realms:
                    realm = realms[0]
                    name = realm.get("name", {}).get("en_US", "Unknown")
                    slug = realm.get("slug", "Unknown")
                    print(f"  {i+1}. {name} (slug: {slug}) - ID: {realm_data.get('id')}")
    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    print("=== Testing realm search with correct authentication ===")
    
    # Try the original slug
    print("\n1. Trying original slug 'twisting-nether':")
    realm_id = get_connected_realm_id("twisting-nether")
    print("Connected realm ID:", realm_id)
    
    # Try searching by name
    print("\n2. Searching by name 'Twisting Nether':")
    realm_id = search_realm_by_name("Twisting Nether")
    print("Connected realm ID:", realm_id)
    
    # Try searching by partial name
    print("\n3. Searching by partial name 'twisting':")
    realm_id = search_realm_by_name("twisting")
    print("Connected realm ID:", realm_id)
    
    # List some realms to see what's available
    print("\n4. Listing first 20 realms:")
    list_all_realms(limit=20)
