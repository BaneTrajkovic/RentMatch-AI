from google import genai
from google.genai import types
from typing import Optional
from .models import ChatbotConversation, ChatbotMessage
import constants

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
