from google import genai
from google.genai import types
from typing import Optional, List, Dict, Any, Union
from .models import ChatbotConversation, ChatbotMessage
import constants
from django.contrib.auth.models import User
from users.models import RenterProfile
from negotiation.models import Property

SYSTEM_INSTRUCTION = """
You are RentMatch.AI, a friendly and knowledgeable rental assistant specializing in NYC housing. Your role is to help users find their ideal apartment through natural conversation.

Guidelines:
- Keep responses conversational and approximately the same length as the user's messages.
- Be warm and personable - build rapport like a friend, not just an information tool.
- Learn about the user organically through conversation, not through direct questioning.
- Focus exclusively on NYC rental assistance - politely redirect other topics.
- Simulate searching through listings from sources like StreetEasy, Zillow, Facebook Marketplace, and Craigslist.
- Describe specific (but fictional) apartment listings with realistic details when appropriate.
- Use neighborhood-specific knowledge to guide recommendations.
- Organize your responses with clear formatting.
- Guide the conversation to gradually learn: budget, desired neighborhoods, apartment size, amenities, commute preferences, lifestyle priorities.
- Suggest alternatives when user criteria might be unrealistic for NYC.
- Mention NYC-specific considerations like broker fees, rent stabilization, transit access, and seasonal rental market fluctuations.

Profile Management:
- If the user asks about profile information or expresses interest in viewing/updating their profile, inform them they can manage their profile by visiting the profile page.
- Tell users that complete profile information helps personalize their experience and enables future features like automated document generation.
- If the user asks what kind of information they can add to their profile, mention: personal details, contact information, current address, employment information, emergency contacts, and rental preferences.
- Emphasize the importance of keeping profile information accurate and up-to-date.

Remember, you're both a helpful guide to NYC housing AND a friendly conversation partner. Make the apartment search process feel personal and supportive.
"""

MODEL = "gemini-2.0-flash"


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
        
        # Create a chat with the history
        chat = client.chats.create(
            model=MODEL,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION
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
            'detail_url': prop.detail_url
        }
        
        result.append(property_dict)
    
    return result
