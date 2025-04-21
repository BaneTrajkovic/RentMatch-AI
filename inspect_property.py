import os
import django
import sys
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from negotiation.models import Property

def inspect_property(zpid=None):
    """
    Inspect a property by zpid and display all its fields
    If no zpid is provided, list the first 10 properties
    """
    if zpid:
        try:
            # Fetch property by zpid
            property_obj = Property.objects.get(zpid=zpid)
            
            # Get all fields and their values
            print("\n=== Property Information ===")
            print(f"ZPID: {property_obj.zpid}")
            print(f"Address: {property_obj.address}")
            print(f"City: {property_obj.city}, {property_obj.state} {property_obj.zipcode}")
            print(f"Price: {property_obj.price} ({property_obj.unformatted_price})")
            print(f"Beds: {property_obj.beds}, Baths: {property_obj.baths}")
            print(f"Type: {property_obj.home_type}")
            print(f"Status: {property_obj.status_text} ({property_obj.status_type})")
            print(f"Days on market: {property_obj.days_on_market}")
            
            print("\n--- Location ---")
            print(f"Latitude: {property_obj.latitude}")
            print(f"Longitude: {property_obj.longitude}")
            
            print("\n--- Features ---")
            print(f"Has Fireplace: {property_obj.has_fireplace}")
            print(f"Has Air Conditioning: {property_obj.has_air_conditioning}")
            print(f"Has Pool: {property_obj.has_pool}")
            print(f"Has Spa: {property_obj.has_spa}")
            
            print("\n--- Images ---")
            print(f"Main Image: {property_obj.main_image_url}")
            print(f"Has Image: {property_obj.has_image}")
            print(f"Has Video: {property_obj.has_video}")
            print(f"Has 3D Model: {property_obj.has_3d_model}")
            
            # Print carousel photos if available
            if property_obj.carousel_photos:
                print("\n--- Carousel Photos ---")
                for i, photo in enumerate(property_obj.carousel_photos, 1):
                    print(f"Photo {i}: {photo.get('url', 'N/A')}")
            
            # Raw JSON data (optional)
            print("\nWould you like to see the complete raw JSON data? (y/n)")
            choice = input().strip().lower()
            if choice == 'y':
                print("\n--- Raw JSON Data ---")
                print(json.dumps(property_obj.raw_json_data, indent=2))
                
        except Property.DoesNotExist:
            print(f"No property found with ZPID: {zpid}")
        except Exception as e:
            print(f"Error retrieving property: {str(e)}")
    else:
        # List first 10 properties
        print("\n=== Available Properties ===")
        properties = Property.objects.all().order_by('-unformatted_price')[:10]
        
        if not properties:
            print("No properties found in the database.")
            return
            
        for i, prop in enumerate(properties, 1):
            print(f"{i}. ZPID: {prop.zpid} - {prop.address} - {prop.price}")
        
        print("\nEnter a ZPID from the list above to inspect it in detail (or press Enter to exit):")
        selected_zpid = input().strip()
        if selected_zpid:
            inspect_property(selected_zpid)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # If zpid is provided as command line argument
        inspect_property(sys.argv[1])
    else:
        # Interactive mode
        print("Welcome to Property Inspector")
        print("Enter a ZPID to inspect (or press Enter to see the first 10 properties):")
        zpid_input = input().strip()
        inspect_property(zpid_input if zpid_input else None) 