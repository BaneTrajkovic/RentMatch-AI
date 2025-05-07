from google import genai
from google.genai import types
from typing import Optional, List, Dict, Any, Union
import constants
from django.contrib.auth.models import User
from users.models import RenterProfile
from .models import Property, PropertyChat, PropertyChatMessage
import json
import re

SYSTEM_INSTRUCTION = """
You are RentMatch.AI's Lease Negotiation Assistant, a specialized AI for facilitating rental negotiations between landlords and tenants. You only respond when specifically asked for help - you'll know this when a message starts with "AI:".

When you do respond, your role is to:

1. Structure negotiations between renters and landlords in a fair, balanced manner
2. Provide legally-informed guidance on lease terms, market standards, and tenant/landlord rights
3. Draft clear, equitable terms based on both parties' stated needs
4. Help finalize digital lease agreements
5. Maintain a neutral, professional tone throughout the process

Guidelines:
- Only respond when a message starts with "AI:" - otherwise remain silent
- Analyze the entire conversation history to understand context before responding
- Use profile information from both renter and landlord to personalize advice
- Organize your responses with clear formatting for readability
- Be concise but thorough
- Aim for fair outcomes that respect both parties' interests
- Clearly separate facts from opinions
- Cite specific rental market data when available
- For lease term drafting, use standard legal language but in plain English
- Help identify points of agreement and disagreement between parties
- Suggest compromises when appropriate

Formatting:
- Use Markdown to format your responses for clarity and readability
- Use headers (## and ###) to separate sections
- Use **bold** for emphasis on important points
- Use bullet lists or numbered lists when appropriate
- Use code blocks for sample lease language or terms
- Use tables for comparing options when relevant
- Format lease templates with clear sections and spacing

Key Topics You Can Assist With:
- Rent amount and payment schedule
- Security deposit terms
- Lease duration and renewal options
- Maintenance responsibilities
- Pet policies
- Subletting rules
- Move-in/move-out conditions
- Utilities and additional fees
- Early termination options
- Property condition assessments

Remember: Your goal is to streamline negotiations to reach mutually beneficial agreements while ensuring all legal and practical aspects of the lease are addressed.
"""

MODEL = "gemini-2.0-flash"

def get_chat_from_conversation(chat: PropertyChat) -> genai.Client.chats:
    """
    Retrieves conversation history from Django models and creates a Gemini chat with that history.
    
    Args:
        chat: The PropertyChat instance
        
    Returns:
        A Gemini chat instance with history loaded
    """
    try:
        # Create client
        client = genai.Client(api_key=constants.GEMINI_API_KEY)
        
        # Get all messages for this conversation
        messages = PropertyChatMessage.objects.filter(chat=chat).order_by('timestamp')
        
        # Format the messages for Gemini
        history = []
        for message in messages:
            # Skip AI messages when building history (they will be included as model responses)
            if message.sender_type == 'bot':
                continue
                
            role = "user"
            if message.user:
                content = f"[{message.sender_type.upper()}] {message.user.username}: {message.content}"
            else:
                content = f"[{message.sender_type.upper()}]: {message.content}"
                
            history.append({
                "role": role,
                "parts": [{"text": content}]
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
    
    except Exception as e:
        # Handle any other errors
        raise Exception(f"Error creating chat from history: {str(e)}")

def should_ai_respond(message: str) -> bool:
    """
    Determines if the AI should respond to a message.
    Returns True if the message starts with "AI:" (case insensitive)
    
    Args:
        message: The message content
    
    Returns:
        Boolean indicating whether AI should respond
    """
    pattern = r"^\s*AI\s*:"
    return bool(re.match(pattern, message, re.IGNORECASE))

def get_user_profile_data(user: User, is_landlord: bool = False) -> dict:
    """
    Gets user profile data for context in AI responses.
    
    Args:
        user: The User object
        is_landlord: Boolean indicating if the user is a landlord
    
    Returns:
        Dictionary with profile information
    """
    profile_data = {
        'username': user.username,
        'email': user.email
    }
    
    # For renters, include additional profile information
    if not is_landlord and hasattr(user, 'renter_profile'):
        renter_profile = user.renter_profile
        profile_data.update({
            'full_name': renter_profile.full_name(),
            'phone_number': renter_profile.phone_number,
            'monthly_income': renter_profile.monthly_income,
            'lease_term_preference': renter_profile.lease_term_preference,
            'move_in_date': renter_profile.move_in_date
        })
    
    return profile_data

def get_property_data(property_obj: Property) -> dict:
    """
    Gets property data for context in AI responses.
    
    Args:
        property_obj: The Property object
    
    Returns:
        Dictionary with property information
    """
    return {
        'address': property_obj.address,
        'price': property_obj.price,
        'beds': property_obj.beds,
        'baths': property_obj.baths,
        'home_type': property_obj.home_type,
    }

def generate_negotiation_response(property_chat: PropertyChat, message: str) -> str:
    """
    Generates an AI response for negotiation assistance.
    
    Args:
        property_chat: The PropertyChat instance
        message: The incoming message
    
    Returns:
        AI response text
    """
    try:
        # Skip AI response if the message doesn't require it
        if not should_ai_respond(message):
            return None
            
        # Get Gemini chat with history
        gemini_chat = get_chat_from_conversation(property_chat)
        
        # Get profiles and property information for context
        landlord_profile = get_user_profile_data(property_chat.landlord, is_landlord=True)
        renter_profile = get_user_profile_data(property_chat.renter)
        property_data = get_property_data(property_chat.property)
        
        # Add context to the message
        context_message = f"""
The following information is for context only:

PROPERTY INFORMATION:
{json.dumps(property_data, indent=2)}

LANDLORD PROFILE:
{json.dumps(landlord_profile, indent=2)}

RENTER PROFILE: 
{json.dumps(renter_profile, indent=2)}

Remember to use Markdown formatting in your response for better readability.

Now please respond to this message:
{message}
"""
        
        # Send to Gemini and get response
        response = gemini_chat.send_message(context_message)
        
        return response.text
        
    except Exception as e:
        return f"An error occurred with the AI assistant: {str(e)}" 