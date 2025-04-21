import json
import statistics
import os
from collections import Counter

def load_zillow_data(filepath):
    """Load the Zillow dataset from a JSON file"""
    print(f"Loading data from {filepath}...")
    with open(filepath, 'r') as f:
        data = json.load(f)
    print(f"Loaded {len(data)} properties")
    return data

def get_price_stats(data):
    """Calculate price statistics from the dataset"""
    prices = [prop.get('unformattedPrice') for prop in data if prop.get('unformattedPrice')]
    if not prices:
        return {"count": 0}
    
    return {
        "count": len(prices),
        "min": min(prices),
        "max": max(prices),
        "mean": statistics.mean(prices),
        "median": statistics.median(prices)
    }

def filter_by_price_range(data, min_price=None, max_price=None):
    """Filter properties by price range"""
    filtered = data
    
    if min_price is not None:
        filtered = [prop for prop in filtered if prop.get('unformattedPrice', 0) >= min_price]
    
    if max_price is not None:
        filtered = [prop for prop in filtered if prop.get('unformattedPrice', 0) <= max_price]
    
    return filtered

def filter_by_beds_baths(data, min_beds=None, min_baths=None):
    """Filter properties by minimum bedrooms and bathrooms"""
    filtered = data
    
    if min_beds is not None:
        filtered = [prop for prop in filtered if prop.get('beds', 0) >= min_beds]
    
    if min_baths is not None:
        filtered = [prop for prop in filtered if prop.get('baths', 0) >= min_baths]
    
    return filtered

def filter_by_location(data, location):
    """Filter properties by location (case-insensitive partial match)"""
    location = location.lower()
    return [prop for prop in data if location in prop.get('address', '').lower()]

def get_location_distribution(data):
    """Get distribution of properties by city"""
    cities = [prop.get('addressCity') for prop in data if prop.get('addressCity')]
    return Counter(cities).most_common(20)

def get_bedroom_distribution(data):
    """Get distribution of properties by number of bedrooms"""
    beds = [prop.get('beds') for prop in data if prop.get('beds')]
    return Counter(beds).most_common()

def print_property_sample(properties, count=5):
    """Print a sample of properties"""
    for i, prop in enumerate(properties[:count]):
        address = prop.get('address', 'Unknown')
        price = prop.get('price', 'Unknown')
        beds = prop.get('beds', 'Unknown')
        baths = prop.get('baths', 'Unknown')
        area = prop.get('area', 'Unknown')
        
        print(f"{i+1}. {address}")
        print(f"   Price: {price}, Beds: {beds}, Baths: {baths}, Area: {area} sq ft")

def main():
    # Path to the Zillow dataset
    filepath = "dataset_zillow-scraper_2025-04-20_23-13-19-128.json"
    
    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}")
        return
    
    # Load the data
    data = load_zillow_data(filepath)
    
    # Calculate and print price statistics
    print("\nPrice Statistics:")
    price_stats = get_price_stats(data)
    print(f"Count: {price_stats['count']}")
    print(f"Min: ${price_stats['min']:,}")
    print(f"Max: ${price_stats['max']:,}")
    print(f"Mean: ${price_stats['mean']:,.2f}")
    print(f"Median: ${price_stats['median']:,.2f}")
    
    # Get location distribution
    print("\nTop 10 Cities:")
    cities = get_location_distribution(data)
    for city, count in cities[:10]:
        print(f"{city}: {count} properties")
    
    # Get bedroom distribution
    print("\nBedroom Distribution:")
    beds_dist = get_bedroom_distribution(data)
    for beds, count in beds_dist:
        print(f"{beds} bedrooms: {count} properties")
    
    # Filter by price range and print sample
    print("\nProperties between $1M and $2M:")
    price_filtered = filter_by_price_range(data, 1000000, 2000000)
    print(f"Found {len(price_filtered)} properties")
    print_property_sample(price_filtered)
    
    # Filter by beds and baths
    print("\nProperties with 3+ bedrooms and 2+ bathrooms:")
    bed_bath_filtered = filter_by_beds_baths(data, 3, 2)
    print(f"Found {len(bed_bath_filtered)} properties")
    print_property_sample(bed_bath_filtered)
    
    # Filter by location
    print("\nProperties in San Francisco:")
    sf_properties = filter_by_location(data, "San Francisco")
    print(f"Found {len(sf_properties)} properties")
    print_property_sample(sf_properties)
    
    # Combine filters
    print("\nLuxury properties (4+ bed, 3+ bath, $3M+):")
    luxury = filter_by_beds_baths(filter_by_price_range(data, 3000000), 4, 3)
    print(f"Found {len(luxury)} luxury properties")
    print_property_sample(luxury)

if __name__ == "__main__":
    main() 