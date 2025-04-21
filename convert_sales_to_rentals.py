import json
import os
import math

def convert_sales_to_rentals(json_file):
    """
    Convert all properties in the Zillow dataset from "For Sale" to "For Rent"
    and adjust prices to reasonable rental values (approx 0.8% of sale price)
    
    Args:
        json_file: Path to the JSON file with property data
    """
    print(f"Converting properties in {json_file}...")
    
    # Load the JSON data
    with open(json_file, 'r') as f:
        properties = json.load(f)
    
    print(f"Loaded {len(properties)} properties")
    
    # Create a backup of the original file
    backup_file = json_file + '.backup'
    if not os.path.exists(backup_file):
        with open(backup_file, 'w') as f:
            json.dump(properties, f)
        print(f"Created backup at {backup_file}")
    
    # Convert each property
    for prop in properties:
        # Skip if already a rental
        if "rent" in prop.get("statusText", "").lower():
            continue
            
        # Get the sale price
        sale_price = prop.get("unformattedPrice", 0)
        if not sale_price:
            # Try to get price from hdpData
            if "hdpData" in prop and "homeInfo" in prop["hdpData"]:
                sale_price = prop["hdpData"]["homeInfo"].get("price", 0)
        
        # Calculate rental price (0.8% of sale price, rounded to nearest $50)
        if sale_price:
            rental_price = sale_price * 0.008
            # Round to nearest $50
            rental_price = round(rental_price / 50) * 50
            # Ensure minimum rental price
            rental_price = max(rental_price, 1000)
            
            # Update price fields
            prop["unformattedPrice"] = int(rental_price)
            prop["price"] = f"${rental_price:,}/mo"
            
            # If rentZestimate exists in hdpData, use it instead
            if "hdpData" in prop and "homeInfo" in prop["hdpData"] and "rentZestimate" in prop["hdpData"]["homeInfo"]:
                rent_zestimate = prop["hdpData"]["homeInfo"]["rentZestimate"]
                if rent_zestimate and rent_zestimate > 500:  # Sanity check
                    prop["unformattedPrice"] = rent_zestimate
                    prop["price"] = f"${rent_zestimate:,}/mo"
                    # Also update the price in homeInfo
                    prop["hdpData"]["homeInfo"]["price"] = rent_zestimate
            else:
                # Update the price in homeInfo if it exists
                if "hdpData" in prop and "homeInfo" in prop["hdpData"]:
                    prop["hdpData"]["homeInfo"]["price"] = int(rental_price)
        
        # Update status fields
        prop["rawHomeStatusCd"] = "ForRent"
        prop["marketingStatusSimplifiedCd"] = "For Rent by Agent"
        prop["statusType"] = "FOR_RENT"
        
        # Update statusText based on property type
        current_status = prop.get("statusText", "").lower()
        if "house" in current_status:
            prop["statusText"] = "House for rent"
        elif "condo" in current_status:
            prop["statusText"] = "Condo for rent"
        elif "apartment" in current_status:
            prop["statusText"] = "Apartment for rent"
        elif "townhouse" in current_status:
            prop["statusText"] = "Townhouse for rent"
        else:
            prop["statusText"] = "Home for rent"
        
        # Update homeStatus in hdpData if it exists
        if "hdpData" in prop and "homeInfo" in prop["hdpData"]:
            prop["hdpData"]["homeInfo"]["homeStatus"] = "FOR_RENT"
            prop["hdpData"]["homeInfo"]["homeStatusForHDP"] = "FOR_RENT"
    
    # Save the modified data
    with open(json_file, 'w') as f:
        json.dump(properties, f)
    
    print(f"Converted {len(properties)} properties to rentals")
    print(f"Done! Modified JSON file saved to {json_file}")

if __name__ == "__main__":
    json_file = "dataset_zillow-scraper_2025-04-20_23-13-19-128.json"
    convert_sales_to_rentals(json_file) 