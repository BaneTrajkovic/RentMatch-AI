import os
import json
from chatbot.zillow_api import ZillowScraper

def test_local_zillow_data():
    """Test loading and filtering Zillow data from the local JSON file"""
    
    # Initialize the ZillowScraper
    scraper = ZillowScraper()
    
    # Verify the JSON file exists
    json_file = scraper.json_data_file
    print(f"Looking for JSON file: {json_file}")
    
    if not os.path.exists(json_file):
        print(f"ERROR: JSON file not found at {json_file}")
        return False
    
    print(f"JSON file found: {os.path.getsize(json_file) / (1024 * 1024):.2f} MB")
    
    # Load the first few items to verify file structure
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        print(f"Successfully loaded JSON data with {len(data)} listings")
        
        # Display info about the first few listings
        for i, listing in enumerate(data[:3]):
            address = listing.get('address', 'Unknown')
            price = listing.get('price', 'Unknown')
            beds = listing.get('beds', 'Unknown')
            baths = listing.get('baths', 'Unknown')
            
            print(f"{i+1}. {address} - {price}, {beds} bed, {baths} bath")
        
        # Test search for CA properties
        print("\nTesting search for California properties:")
        ca_url = "https://www.zillow.com/ca/"
        ca_results = scraper.search_listings(ca_url, max_results=5)
        
        print(f"Found {len(ca_results)} California properties")
        for i, listing in enumerate(ca_results):
            address = listing.get('address', 'Unknown')
            price = listing.get('price', 'Unknown')
            beds = listing.get('beds', 'Unknown')
            baths = listing.get('baths', 'Unknown')
            
            print(f"{i+1}. {address} - {price}, {beds} bed, {baths} bath")
        
        # Test search with price range
        print("\nTesting search with price range (1M-2M):")
        # Using an explicit price filter format
        price_url = "https://www.zillow.com/homes/for_sale/?min_price=1000000&max_price=2000000"
        price_results = scraper.search_listings(price_url, max_results=5)
        
        print(f"Found {len(price_results)} properties in price range")
        for i, listing in enumerate(price_results):
            address = listing.get('address', 'Unknown')
            price = listing.get('price', 'Unknown')
            unformatted_price = listing.get('unformattedPrice', 'Unknown')
            beds = listing.get('beds', 'Unknown')
            baths = listing.get('baths', 'Unknown')
            
            print(f"{i+1}. {address} - {price} (${unformatted_price}), {beds} bed, {baths} bath")
        
        # Manually filter data
        print("\nManually filtering for 3+ bedroom properties:")
        three_bed_properties = []
        for listing in data:
            beds = listing.get('beds', 0)
            if beds >= 3:
                three_bed_properties.append(listing)
                if len(three_bed_properties) >= 5:
                    break
        
        print(f"Found {len(three_bed_properties)} properties with 3+ bedrooms")
        for i, listing in enumerate(three_bed_properties):
            address = listing.get('address', 'Unknown')
            price = listing.get('price', 'Unknown')
            beds = listing.get('beds', 'Unknown')
            baths = listing.get('baths', 'Unknown')
            
            print(f"{i+1}. {address} - {price}, {beds} bed, {baths} bath")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to process JSON data: {str(e)}")
        return False

if __name__ == "__main__":
    test_local_zillow_data() 