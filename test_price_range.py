import json
import os
from chatbot.zillow_api import ZillowScraper

def test_price_range_filtering():
    """Test filtering based on price range"""
    
    # Initialize the ZillowScraper
    scraper = ZillowScraper()
    
    # Get the path to the JSON file
    json_file = scraper.json_data_file
    print(f"Using JSON file: {json_file}")
    
    # Load all data
    with open(json_file, 'r') as f:
        all_data = json.load(f)
    
    print(f"Loaded {len(all_data)} properties")
    
    # Filter for properties between 1M and 2M
    min_price = 1000000
    max_price = 2000000
    
    in_range = []
    for prop in all_data:
        price = prop.get('unformattedPrice', 0)
        if min_price <= price <= max_price:
            in_range.append(prop)
    
    print(f"Found {len(in_range)} properties in price range ${min_price:,} - ${max_price:,}")
    
    # Display the first 5 properties in range
    for i, prop in enumerate(in_range[:5]):
        address = prop.get('address', 'Unknown')
        price = prop.get('price', 'Unknown')
        beds = prop.get('beds', 'Unknown')
        baths = prop.get('baths', 'Unknown')
        
        print(f"{i+1}. {address} - {price}, {beds} bed, {baths} bath")
    
    return len(in_range) > 0

if __name__ == "__main__":
    test_price_range_filtering() 