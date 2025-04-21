import os
import sys
from google import genai
from google.genai import types
import json
import constants
# Set your API key
GEMINI_API_KEY = constants.GEMINI_API_KEY  # Add your API key here or set it as an environment variable

# Define function declaration for property search
SEARCH_PROPERTIES_DECLARATION = {
    "name": "search_properties",
    "description": "Searches for available rental properties based on specified criteria",
    "parameters": {
        "type": "object",
        "properties": {
            "address_keywords": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "List of keywords to search in the address (e.g., neighborhood names, streets, landmarks)"
            },
            "min_price": {
                "type": "number",
                "description": "Minimum monthly rent in USD"
            },
            "max_price": {
                "type": "number",
                "description": "Maximum monthly rent in USD"
            },
            "home_type": {
                "type": "string",
                "description": "Type of property (Apartment, House, Condo, etc.)"
            },
            "beds": {
                "type": "integer",
                "description": "Number of bedrooms"
            },
            "baths": {
                "type": "number",
                "description": "Number of bathrooms"
            },
            "amenities": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ["fireplace", "pool", "spa", "air_conditioning"]
                },
                "description": "List of desired amenities"
            }
        },
        "required": []
    }
}

# Sample data for testing - these would normally come from your database
SAMPLE_PROPERTIES = [
    {
        'zpid': '123456',
        'address': '123 Main St, Manhattan, NY 10001',
        'street_address': '123 Main St',
        'city': 'New York',
        'state': 'NY',
        'zipcode': '10001',
        'price': '$3,200/mo',
        'unformatted_price': 3200.0,
        'beds': 2,
        'baths': 1.5,
        'home_type': 'Apartment',
        'amenities': {
            'fireplace': False,
            'pool': False,
            'spa': False,
            'air_conditioning': True
        },
        'main_image_url': 'https://example.com/image1.jpg',
        'detail_url': 'https://example.com/property/123456'
    },
    {
        'zpid': '234567',
        'address': '456 Park Ave, Brooklyn, NY 11201',
        'street_address': '456 Park Ave',
        'city': 'New York',
        'state': 'NY',
        'zipcode': '11201',
        'price': '$2,800/mo',
        'unformatted_price': 2800.0,
        'beds': 1,
        'baths': 1.0,
        'home_type': 'Condo',
        'amenities': {
            'fireplace': False,
            'pool': True,
            'spa': False,
            'air_conditioning': True
        },
        'main_image_url': 'https://example.com/image2.jpg',
        'detail_url': 'https://example.com/property/234567'
    },
    {
        'zpid': '345678',
        'address': '789 East Village, Manhattan, NY 10009',
        'street_address': '789 East Village',
        'city': 'New York',
        'state': 'NY',
        'zipcode': '10009',
        'price': '$2,800/mo',
        'unformatted_price': 2800.0,
        'beds': 2,
        'baths': 2.0,
        'home_type': 'Apartment',
        'amenities': {
            'fireplace': True,
            'pool': False,
            'spa': False,
            'air_conditioning': True
        },
        'main_image_url': 'https://example.com/image3.jpg',
        'detail_url': 'https://example.com/property/345678'
    }
]

def mock_search_properties(
    address_keywords=None,
    min_price=None,
    max_price=None,
    home_type=None,
    beds=None,
    baths=None,
    amenities=None
):
    """Mock implementation of the search_properties function for testing."""
    print(f"Mock search with params: address_keywords={address_keywords}, min_price={min_price}, max_price={max_price}, home_type={home_type}, beds={beds}, baths={baths}, amenities={amenities}")
    
    # Apply filters to the sample properties
    results = SAMPLE_PROPERTIES.copy()
    
    # Filter by address keywords
    if address_keywords and len(address_keywords) > 0:
        filtered_results = []
        for prop in results:
            address_lower = prop['address'].lower()
            if all(keyword.lower() in address_lower for keyword in address_keywords):
                filtered_results.append(prop)
        results = filtered_results
    
    # Filter by price
    if min_price is not None:
        results = [prop for prop in results if prop['unformatted_price'] >= min_price]
    if max_price is not None:
        results = [prop for prop in results if prop['unformatted_price'] <= max_price]
    
    # Filter by property type
    if home_type:
        results = [prop for prop in results if prop['home_type'].lower() == home_type.lower()]
    
    # Filter by beds
    if beds is not None:
        results = [prop for prop in results if prop['beds'] >= beds]
    
    # Filter by baths
    if baths is not None:
        results = [prop for prop in results if prop['baths'] >= baths]
    
    # Filter by amenities
    if amenities and len(amenities) > 0:
        filtered_results = []
        for prop in results:
            has_all_amenities = True
            for amenity in amenities:
                if not prop['amenities'].get(amenity, False):
                    has_all_amenities = False
                    break
            if has_all_amenities:
                filtered_results.append(prop)
        results = filtered_results
    
    return results

def format_property_results(properties):
    """
    Formats property search results into a user-friendly markdown string.
    """
    if not properties:
        return "No properties found matching your criteria."
    
    markdown = "## Properties Found\n\n"
    
    for i, prop in enumerate(properties[:5]):
        markdown += f"### {i+1}. {prop['address']}\n\n"
        
        if prop['main_image_url']:
            markdown += f"![Property Image]({prop['main_image_url']})\n\n"
        
        markdown += f"**Price:** {prop['price']}\n"
        markdown += f"**Bedrooms:** {prop['beds']}\n"
        markdown += f"**Bathrooms:** {prop['baths']}\n"
        markdown += f"**Type:** {prop['home_type']}\n\n"
        
        # Add amenities if any are available
        amenities = []
        for amenity, has_it in prop['amenities'].items():
            if has_it:
                amenities.append(amenity.replace('_', ' ').title())
        
        if amenities:
            markdown += f"**Amenities:** {', '.join(amenities)}\n\n"
        
        if prop['detail_url']:
            markdown += f"[View Details]({prop['detail_url']})\n\n"
        
        # Add separator between properties
        if i < len(properties[:5]) - 1:
            markdown += "---\n\n"
    
    if len(properties) > 5:
        markdown += f"\n*Showing 5 of {len(properties)} properties found.*\n"
    
    return markdown

def test_function_calling(message):
    """
    Test the Gemini function calling with a specific message.
    
    Args:
        message: The message to send
    """
    try:
        # Set API key
        api_key = GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("Error: GEMINI_API_KEY is not set. Please set it in the script or as an environment variable.")
            return None
        
        # Create client
        client = genai.Client(api_key=api_key)
        
        # System instruction for the model
        system_instruction = """
        You are RentMatch.AI, a friendly and knowledgeable rental assistant specializing in NYC housing. Your role is to help users find their ideal apartment through natural conversation.

        When users ask about finding apartments or rentals, use the search_properties function to provide real listings.
        When describing properties, use the formatted markdown results directly from the function call.
        """
        
        # Set up the tools configuration
        tools = types.Tool(function_declarations=[SEARCH_PROPERTIES_DECLARATION])
        
        # Create a new chat
        chat = client.chats.create(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=[tools]
            )
        )
        
        # Send the message to the model
        print(f"Sending message: '{message}'")
        response = chat.send_message(message)
        
        # Check if the response contains a function call
        function_called = False
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    function_called = True
                    function_call = part.function_call
                    print(f"\nFunction call detected: {function_call.name}")
                    print(f"Arguments: {json.dumps(function_call.args, indent=2)}")
                    
                    # If it's our search_properties function
                    if function_call.name == "search_properties":
                        # Call our mock function with the provided args
                        search_results = mock_search_properties(**function_call.args)
                        
                        # Format the results
                        formatted_results = format_property_results(search_results)
                        print("\nFormatted Results:")
                        print(formatted_results)
                        
                        # Create a content object with the function call response
                        function_response = {
                            "role": "function",
                            "name": function_call.name,
                            "parts": [{"text": formatted_results}]
                        }
                        
                        # Send the function execution result back to continue the conversation
                        print("\nSending function results back to model...")
                        final_response = chat.send_message(formatted_results)
                        
                        print("\n--- FINAL RESPONSE ---\n")
                        print(final_response.text)
                        print("\n--- END FINAL RESPONSE ---\n")
                        return final_response.text
        
        # If no function call was made, just return the text response
        if not function_called:
            print("\nNo function call detected. Direct response:")
            print("\n--- RESPONSE ---\n")
            print(response.text)
            print("\n--- END RESPONSE ---\n")
            return response.text
        
    except Exception as e:
        print(f"Error testing function calling: {str(e)}")
        return None

if __name__ == "__main__":
    # Check if command line arguments are provided
    if len(sys.argv) < 2:
        print("Usage: python test_function_calling_standalone.py <message>")
        print("Example: python test_function_calling_standalone.py 'Show me 2-bedroom apartments in Manhattan under $3000'")
        
        # Use default value if no argument provided
        message = "Show me 2-bedroom apartments in Manhattan under $3000"
    else:
        message = sys.argv[1]
    
    # Run the test
    test_function_calling(message) 