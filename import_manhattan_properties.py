import json
import os
import django
import sys
import traceback

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from negotiation.models import Property
from django.db import transaction

def import_manhattan_properties():
    """Import properties from the manhattan_4000.json file"""
    # Load the JSON data from file
    try:
        print("Opening JSON file...")
        json_file_path = 'json_data/manhattan_4000.json'
        with open(json_file_path, 'r') as f:
            print("Loading JSON data...")
            data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File {json_file_path} not found")
        return
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON format: {e}")
        return
    except Exception as e:
        print(f"ERROR: Unexpected error reading JSON file: {e}")
        return

    # Track counts
    total_properties = len(data) if isinstance(data, list) else 1
    print(f"Found {total_properties} properties in JSON data")
    created_count = 0
    skipped_count = 0
    error_count = 0

    # Process each property in the JSON
    for index, property_data in enumerate((data if isinstance(data, list) else [data])):
        try:
            # Extract zpid and validate
            zpid = property_data.get('zpid', '')
            if not zpid:
                print(f"Skipping property at index {index}: No zpid")
                skipped_count += 1
                continue
                
            # Check if property already exists
            if Property.objects.filter(zpid=zpid).exists():
                print(f"Property with zpid {zpid} already exists, skipping")
                skipped_count += 1
                continue
                
            # Validate required data
            if not property_data.get('address'):
                print(f"Warning: Property {zpid} has no address")
            
            # Create the property instance using the from_json method
            with transaction.atomic():
                property_obj = Property.from_json(property_data)
                property_obj.save()
                
            created_count += 1
            
            # Print progress periodically
            if created_count % 100 == 0 or index == 0:
                print(f"Created {created_count}/{total_properties} properties so far...")
                
        except Exception as e:
            error_count += 1
            print(f"Error processing property at index {index}:")
            print(f"  Type: {type(e).__name__}")
            print(f"  Message: {str(e)}")
            if hasattr(e, '__traceback__'):
                traceback.print_tb(e.__traceback__)
            
            # If we hit too many errors, stop processing
            if error_count > 50:
                print("Too many errors, stopping import process")
                break

    print(f"\nImport Summary:")
    print(f"  Total in file: {total_properties}")
    print(f"  Created: {created_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Errors: {error_count}")

if __name__ == '__main__':
    print("Starting Manhattan property import process...")
    try:
        import_manhattan_properties()
        print("Import process completed")
    except Exception as e:
        print(f"Fatal error in import process: {e}")
        traceback.print_exc()
        sys.exit(1) 