from google import genai
from google.genai import types
from typing import Optional, List, Dict, Any, Union
from .models import ChatbotConversation, ChatbotMessage
import constants
from django.contrib.auth.models import User
from users.models import RenterProfile
from negotiation.models import Property
import json
import re

SYSTEM_INSTRUCTION = """
You are RentMatch.AI, a friendly and knowledgeable rental assistant specializing in NYC housing. Your role is to help users find their ideal apartment through natural conversation.

Guidelines:
- Keep responses conversational and approximately the same length as the user's messages.
- Be warm and personable - build rapport like a friend, not just an information tool.
- Learn about the user organically through conversation, not through direct questioning.
- Focus exclusively on NYC rental assistance - politely redirect other topics.
- When users ask about finding apartments or rentals, use the search_properties function to provide real listings.
- When describing properties, you MUST use the exact formatted markdown results returned by the function call.
- CRITICAL: Never reformat, summarize, or modify the property listings returned by search_properties function.
- CRITICAL: Always include ALL property images exactly as they appear in the function results - do not remove or rewrite the markdown image syntax.
- Use neighborhood-specific knowledge to guide recommendations.
- Organize your responses with clear formatting.
- Guide the conversation to gradually learn: budget, desired neighborhoods, apartment size, amenities, commute preferences, lifestyle priorities.
- Suggest alternatives when user criteria might be unrealistic for NYC.
- Mention NYC-specific considerations like broker fees, rent stabilization, transit access, and seasonal rental market fluctuations.

Using the search_properties Function:
- When a user asks about finding apartments or provides search criteria, always use the search_properties function.
- Translate user requests into appropriate search parameters (address_keywords, min_price, max_price, home_type, beds, baths, amenities).
- If the user provides vague criteria, ask clarifying questions before searching.
- Always use the function call results to guide your response rather than making up fictional listings.
- You MUST include the ENTIRE markdown response from the function including all images and formatting without modification.
- NEVER rewrite or summarize property listings in your own words - use the exact markdown returned by the function.

Profile Management:
- If the user asks about profile information or expresses interest in viewing/updating their profile, inform them they can manage their profile by visiting the profile page.
- Tell users that complete profile information helps personalize their experience and enables future features like automated document generation.
- If the user asks what kind of information they can add to their profile, mention: personal details, contact information, current address, employment information, emergency contacts, and rental preferences.
- Emphasize the importance of keeping profile information accurate and up-to-date.

Remember, you're both a helpful guide to NYC housing AND a friendly conversation partner. Make the apartment search process feel personal and supportive.
"""

MODEL = "gemini-2.0-flash"

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

def get_chat_from_conversation(conversation: ChatbotConversation) -> genai.Client.chats:
    """
    Retrieves conversation history from Django models and creates a Gemini chat with that history.
    
    Args:
        client: The Gemini client
        model_name: Name of the Gemini model to use
        conversation_id: Primary key of the ChatbotConversation in the database
        
    Returns:
        A Gemini chat instance with history loaded
    """
    try:
        # Create client
        client = genai.Client(api_key=constants.GEMINI_API_KEY)
        
        # Get all messages for this conversation
        messages = ChatbotMessage.objects.filter(conversation=conversation).order_by('timestamp')
        
        # Format the messages for Gemini
        history = []
        for message in messages:
            history.append({
                "role": message.role,
                "parts": [{"text": message.content}]
            })
        
        # Set up the tools configuration
        tools = types.Tool(function_declarations=[SEARCH_PROPERTIES_DECLARATION])
        
        # Create a chat with the history and tools
        chat = client.chats.create(
            model=MODEL,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                tools=[tools]
            ),
            history=history
        )
        
        return chat
    
    except ChatbotConversation.DoesNotExist:
        # Handle the case where the conversation doesn't exist
        raise ValueError(f"Conversation is not found")
    
    except Exception as e:
        # Handle any other errors
        raise Exception(f"Error creating chat from history: {str(e)}")

def send_message_with_function_calling(chat, user_message: str) -> str:
    """
    Sends a message to the Gemini chat with function calling capability.
    
    Args:
        chat: The Gemini chat instance
        user_message: The user's message text
        
    Returns:
        The response text from the model
    """
    try:
        # Send the message to the model
        response = chat.send_message(user_message)
        
        # Check if the response contains a function call
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    function_call = part.function_call
                    
                    # Handle the function call based on its name
                    if function_call.name == "search_properties":
                        # Execute the search_properties function with the provided args
                        search_results = search_properties(**function_call.args)
                        
                        # Format the search results into a user-friendly markdown response
                        formatted_results = format_property_results(search_results)
                        
                        # Add an instruction to preserve the markdown
                        preservation_instruction = (
                            "IMPORTANT: The property listings above include markdown formatting and images. "
                            "Include this EXACT markdown in your response without modification. "
                            "Do not rewrite, summarize, or change the markdown image syntax in any way. "
                            "Begin your response with the property listings exactly as shown above, then continue your conversation naturally."
                        )
                        
                        # Send the function execution result back to continue the conversation
                        final_response = chat.send_message(formatted_results + "\n\n" + preservation_instruction)
                        
                        # Extract just the model's response without our instruction
                        response_text = final_response.text
                        if preservation_instruction in response_text:
                            response_text = response_text.replace(preservation_instruction, "").strip()
                        
                        # Check if the result contains our markers
                        start_marker = "<!-- PROPERTY_RESULTS_START -->"
                        end_marker = "<!-- PROPERTY_RESULTS_END -->"
                        
                        # Check if the response preserved our markers and includes image markdown
                        if start_marker not in response_text or end_marker not in response_text or not re.search(r'!\[.*?\]\(.*?\)', response_text):
                            # Extract the original formatted results with markers
                            original_markdown = formatted_results
                            
                            # Try again with stricter instructions
                            strict_instruction = (
                                "CRITICAL: Your response MUST include the exact property listings markdown with images. "
                                "Copy and paste the ENTIRE markdown as shown below at the beginning of your response:\n\n" +
                                formatted_results + "\n\n" +
                                "After this, you may add your own message to continue the conversation."
                            )
                            
                            retry_response = chat.send_message(strict_instruction)
                            response_text = retry_response.text
                            
                            # If still no proper markdown with images, combine the original markdown with a generic response
                            if start_marker not in response_text or end_marker not in response_text or not re.search(r'!\[.*?\]\(.*?\)', response_text):
                                # Extract any conversational text from the model's response
                                conversation_text = "Here are the properties that match your search criteria. Let me know if any of these interest you or if you'd like to refine your search."
                                
                                # Remove markers for final output
                                clean_markdown = original_markdown.replace(start_marker, "").replace(end_marker, "").strip()
                                
                                # Combine the original markdown with the conversation text
                                return clean_markdown + "\n\n" + conversation_text
                            
                        # If markers are present, clean up the response by removing markers
                        response_text = response_text.replace(start_marker, "").replace(end_marker, "")
                        
                        return response_text
        
        # If no function call was made, just return the text response
        return response.text
    
    except Exception as e:
        # Handle any errors
        raise Exception(f"Error processing message with function calling: {str(e)}")

def format_property_results(properties: List[Dict[str, Any]]) -> str:
    """
    Formats property search results into a user-friendly markdown string.
    
    Args:
        properties: List of property dictionaries from search_properties
        
    Returns:
        A markdown formatted string with property details
    """
    if not properties:
        return "No properties found matching your criteria."
    
    # Add a unique marker for the start of property results
    marker_start = "<!-- PROPERTY_RESULTS_START -->"
    marker_end = "<!-- PROPERTY_RESULTS_END -->"
    
    markdown = f"{marker_start}\n## Properties Found\n\n"
    
    for i, prop in enumerate(properties[:5]):  # Limit to 5 properties to avoid overwhelming responses
        markdown += f"### {i+1}. {prop['address']}\n\n"
        
        # Display main image
        if prop['main_image_url']:
            markdown += f"![Property Image]({prop['main_image_url']})\n\n"
            
        # Display up to 2 additional carousel images if available
        if prop.get('carousel_photos') and isinstance(prop['carousel_photos'], list) and len(prop['carousel_photos']) > 0:
            carousel_photos = prop['carousel_photos']
            # Display up to 2 additional images (3 total including main)
            for photo_idx, photo in enumerate(carousel_photos[:2]):
                if photo and isinstance(photo, dict) and 'url' in photo:
                    markdown += f"![Property Image {photo_idx+2}]({photo['url']})\n\n"
        
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
    
    markdown += f"\n{marker_end}"
    
    return markdown

def get_renter_profile_data(user: User) -> dict:
    """
    Retrieves the renter profile data for the given user.
    
    Args:
        user: The user whose profile data to retrieve
        
    Returns:
        A dictionary containing the user's profile data
    """
    try:
        # Get the renter profile for this user
        profile = RenterProfile.objects.get(user=user)
        
        # Format the profile data for use in document generation
        profile_data = {
            "user_info": {
                "username": user.username,
                "email": user.email,
                "full_name": profile.full_name(),
                "first_name": profile.first_name,
                "last_name": profile.last_name
            },
            "personal_info": {
                "date_of_birth": profile.date_of_birth.strftime('%Y-%m-%d') if profile.date_of_birth else "",
                "phone_number": profile.phone_number
            },
            "address": {
                "street": profile.current_address,
                "city": profile.current_city,
                "state": profile.current_state,
                "zip_code": profile.current_zip_code
            },
            "employment": {
                "employer": profile.employer_name,
                "title": profile.job_title,
                "income": float(profile.monthly_income) if profile.monthly_income else 0,
                "start_date": profile.employment_start_date.strftime('%Y-%m-%d') if profile.employment_start_date else ""
            },
            "additional_info": {
                "ssn_last_four": profile.ssn_last_four,
                "emergency_contact": profile.emergency_contact_name,
                "emergency_contact_phone": profile.emergency_contact_phone
            },
            "preferences": {
                "lease_term": profile.lease_term_preference,
                "move_in_date": profile.move_in_date.strftime('%Y-%m-%d') if profile.move_in_date else ""
            }
        }
        
        return profile_data
    
    except RenterProfile.DoesNotExist:
        # Return empty data if profile doesn't exist
        return {
            "user_info": {
                "username": user.username,
                "email": user.email,
                "full_name": user.username,
                "first_name": "",
                "last_name": ""
            },
            "personal_info": {},
            "address": {},
            "employment": {},
            "additional_info": {},
            "preferences": {}
        }
    
    except Exception as e:
        # Handle any other errors
        raise Exception(f"Error retrieving profile data: {str(e)}")

def generate_lease_document(user: User, property_data: dict) -> str:
    """
    Generates a lease document using Gemini API based on the user's profile and property data.
    
    Args:
        user: The user (renter) for whom to generate the lease
        property_data: Information about the property being leased
        
    Returns:
        A string containing the generated lease document
    """
    try:
        # Get renter profile data
        renter_data = get_renter_profile_data(user)
        
        # Create client
        client = genai.Client(api_key=constants.GEMINI_API_KEY)
        
        # Create a system prompt for generating the lease
        lease_system_prompt = """
        You are a legal document generator specializing in creating detailed, legally-sound residential lease agreements.
        Generate a complete lease agreement using the property and tenant information provided.
        The lease should include:
        
        1. Standard lease sections (parties, property description, term, rent, security deposit, utilities, etc.)
        2. Tenant and landlord responsibilities
        3. Rules and regulations
        4. Default and remedies
        5. Applicable state/local laws and disclosures
        6. Signature blocks
        
        Use the exact tenant and property information provided. Format the document properly with clear section headings
        and professional legal language suitable for a binding contract.
        """
        
        # Combine the data
        prompt = f"""
        Generate a comprehensive lease agreement using the following information:
        
        PROPERTY INFORMATION:
        {property_data}
        
        TENANT INFORMATION:
        {renter_data}
        
        Format the lease as a complete, legally-compliant document ready for signatures.
        """
        
        # Generate the lease document
        response = client.generate_content(
            model=MODEL,
            generation_config=types.GenerateContentConfig(
                system_instruction=lease_system_prompt
            ),
            contents=[{"role": "user", "parts": [{"text": prompt}]}]
        )
        
        return response.text
    
    except Exception as e:
        # Handle any errors
        raise Exception(f"Error generating lease document: {str(e)}")

def detect_profile_update_intent(message: str) -> bool:
    """
    Detects if the user message indicates an intent to update their profile information.
    
    Args:
        message: The user's message
        
    Returns:
        True if the message indicates profile update intent, False otherwise
    """
    profile_keywords = [
        'update my profile', 
        'edit my profile', 
        'change my profile', 
        'modify my profile',
        'update profile', 
        'edit profile', 
        'change profile',
        'update my information', 
        'edit my information',
        'update my details', 
        'edit my details',
        'update my personal information',
        'edit my personal information'
    ]
    
    message_lower = message.lower()
    
    for keyword in profile_keywords:
        if keyword in message_lower:
            return True
    
    return False

def search_properties(
    address_keywords: List[str] = None,
    min_price: float = None,
    max_price: float = None,
    home_type: str = None,
    beds: int = None,
    baths: float = None,
    amenities: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Search properties based on multiple criteria and return them as a list of dictionaries.
    
    Args:
        address_keywords: List of strings to search in address fields (case-insensitive)
                         Properties must contain ALL keywords across their address fields
        min_price: Minimum price for filtering
        max_price: Maximum price for filtering
        home_type: Type of property (Apartment, House, etc.)
        beds: Number of bedrooms
        baths: Number of bathrooms
        amenities: List of amenities to filter by (fireplace, pool, spa, air_conditioning)
        
    Returns:
        List of dictionaries containing property data
    """
    # Use the Property model's search method to get the QuerySet
    properties = Property.search_properties(
        address_keywords=address_keywords,
        min_price=min_price,
        max_price=max_price,
        home_type=home_type,
        beds=beds,
        baths=baths,
        amenities=amenities
    )
    
    # Convert QuerySet to a list of dictionaries
    result = []
    for prop in properties:
        property_dict = {
            'zpid': prop.zpid,
            'address': prop.address,
            'street_address': prop.street_address,
            'city': prop.city,
            'state': prop.state,
            'zipcode': prop.zipcode,
            'price': prop.price,
            'unformatted_price': float(prop.unformatted_price) if prop.unformatted_price else None,
            'beds': prop.beds,
            'baths': prop.baths,
            'home_type': prop.home_type,
            'amenities': {
                'fireplace': prop.has_fireplace,
                'pool': prop.has_pool,
                'spa': prop.has_spa,
                'air_conditioning': prop.has_air_conditioning
            },
            'main_image_url': prop.main_image_url,
            'detail_url': prop.detail_url,
            'carousel_photos': prop.carousel_photos
        }
        
        result.append(property_dict)
    
    return result
