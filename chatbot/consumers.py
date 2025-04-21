import json
from channels.generic.websocket import WebsocketConsumer
from .models import ChatbotConversation, ChatbotMessage
from .helpers import (
    get_chat_from_conversation, 
    search_properties, 
    analyze_lease_agreement, 
    suggest_negotiation_strategy,
    parse_search_request
)
from google.genai.types import FunctionCall
import logging
import constants

logger = logging.getLogger(__name__)

CONVERSATION_TITLE = """
Analyze our complete conversation history and create a specific, contextual title that:
1. Reflects the exact topic we've discussed
2. Captures the progression from initial question to current direction
3. Includes any unique aspects or specific approaches mentioned
4. Incorporates the ultimate goal or application I'm working toward
5. Uses terminology specific to our exchange, not generic descriptions

Return only the title text (maximum 40 characters), with no explanations or additional text.
"""

class ChatConsumer(WebsocketConsumer):

    def connect(self):
    
        if self.scope["user"].is_authenticated:
    
            if self.scope["path"] == "/ws/chatbot/new/":
    
                self.conversation = None
                self.chat = None
                self.accept()  # Accept the connection
    
            elif "conversation_id" in self.scope["url_route"]["kwargs"]:
    
                conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
    
                try:
    
                    self.conversation = ChatbotConversation.objects.get(id=conversation_id, user=self.scope["user"])
                    # Always set chat to None to use our direct processing
                    self.chat = None
                    self.accept()  # Accept the connection
    
                except ChatbotConversation.DoesNotExist:
                    
                    self.close()
                    return
            else:
    
                self.close()
    
        else:
    
            self.close()

    
    def receive(self, text_data=None, bytes_data=None):
        try:
            user_message = json.loads(text_data)["message"]
            
            # Create a new conversation on first message if needed
            if self.conversation is None:
                self.conversation = ChatbotConversation.objects.create(user=self.scope["user"])
                # Always set chat to None to use our direct processing
                self.chat = None
                
            # Save user message to database
            ChatbotMessage.objects.create(
                conversation=self.conversation,
                role='user',
                content=user_message
            )
            
            # Show typing indicator to the user
            self.send(text_data=json.dumps({
                "type": "typing_indicator",
                "is_typing": True
            }))
            
            # Always process the user's message directly
            response_text = self._process_direct_query(user_message)
            
            # Save bot response
            ChatbotMessage.objects.create(
                conversation=self.conversation,
                role='model',
                content=response_text
            )
            
            # Hide typing indicator
            self.send(text_data=json.dumps({
                "type": "typing_indicator",
                "is_typing": False
            }))
            
            # Send response to client
            self.send(text_data=json.dumps({
                "type": "chat_message",
                "message": response_text
            }))
            
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")
            self.send(text_data=json.dumps({
                "type": "error",
                "message": f"An error occurred: {str(e)}"
            }))
    
    def handle_function_call(self, function_call: FunctionCall) -> str:
        """
        Handle function calls from the model
        
        Args:
            function_call: The function call object from Gemini
            
        Returns:
            Function response as string
        """
        try:
            function_name = function_call.name
            function_args = json.loads(function_call.args)
            
            if function_name == "search_properties":
                return search_properties(function_args)
            elif function_name == "analyze_lease_agreement":
                return analyze_lease_agreement(function_args)
            elif function_name == "suggest_negotiation_strategy":
                return suggest_negotiation_strategy(function_args)
            else:
                return f"Function {function_name} not implemented"
        
        except Exception as e:
            logger.error(f"Error handling function call: {str(e)}")
            return f"Error handling function call: {str(e)}"
            
    def _process_direct_query(self, user_message: str) -> str:
        """
        Process user query directly when chat API is not available
        
        Args:
            user_message: The user's message
            
        Returns:
            Response based on user's query
        """
        # Check if the message appears to be about property search
        message_lower = user_message.lower()
        if any(term in message_lower for term in ["apartment", "looking for", "find", "bedroom", "bath", "rent", "price", "budget", "house", "property", "home", "condo", "show", "search"]):
            # Extract parameters using our existing function
            params = parse_search_request(user_message)
            # Log the extracted parameters
            logger.info(f"Extracted search params: {params}")
            
            # Get property data
            from .zillow_api import ZillowScraper
            scraper = ZillowScraper()
            properties = scraper.search_by_location(
                location=params.get('location', 'California'),
                min_price=params.get('min_price'),
                max_price=params.get('max_price'),
                min_beds=params.get('min_beds'),
                min_baths=params.get('min_baths'),
                home_type=params.get('home_type'),
                for_rent=True  # Default to rental properties
            )
            
            if properties:
                # Create a custom response with property count and up to 10 properties
                property_count = len(properties)
                max_display = min(10, property_count)
                
                response = f"## Found {property_count} rental properties matching your criteria\n\n"
                
                # Format each property with more details
                for i, prop in enumerate(properties[:max_display]):
                    address = prop.get('address', 'Address not available')
                    price = prop.get('price', 'Price not available')
                    beds = prop.get('beds', 'N/A')
                    baths = prop.get('baths', 'N/A')
                    area = prop.get('area', 'N/A')
                    status = prop.get('statusText', 'Property')
                    url = prop.get('detailUrl', '#')
                    
                    response += f"### {i+1}. [{address}]({url})\n"
                    response += f"**Price:** {price} | **Beds:** {beds} | **Baths:** {baths} | **Area:** {area} sq ft\n"
                    response += f"**Type:** {status}\n\n"
                    
                    # Add image if available
                    if prop.get('imgSrc'):
                        response += f"![Property Image]({prop['imgSrc']})\n\n"
                
                if property_count > max_display:
                    response += f"\n*Showing {max_display} of {property_count} properties.*\n"
                    
                response += "\nWould you like more information about any of these properties? Or would you like to refine your search?"
                return response
            else:
                return "I searched our database but couldn't find any rental properties exactly matching your criteria. Try being more general, for example:\n\n- \"Show me apartments in California\"\n- \"Find rentals under $3,000 per month\"\n- \"Show me homes with at least 3 bedrooms\""
        
        # Check if the message appears to be about lease analysis
        elif any(term in message_lower for term in ["lease", "contract", "agreement", "analyze", "review"]):
            # Use lease analysis
            from .helpers import analyze_lease_agreement
            return analyze_lease_agreement({
                "lease_text": user_message,
                "role": "tenant" if "tenant" in message_lower else "landlord"
            })
        
        # Check if the message appears to be about negotiation
        elif any(term in message_lower for term in ["negotiate", "negotiation", "strategy", "bargain", "deal"]):
            # Use negotiation strategy
            from .helpers import suggest_negotiation_strategy
            return suggest_negotiation_strategy({
                "context": user_message,
                "role": "tenant" if "tenant" in message_lower else "landlord",
                "key_points": ["price", "terms", "conditions"]
            })
            
        else:
            # General help message
            return """
I can help you find rental properties in California. Here are some example queries you can try:

1. "Show me apartments in Napa under $3,000/month"
2. "Find 3-bedroom rentals in San Francisco" 
3. "What condos are available for rent in Sonoma?"
4. "Show me waterfront rental properties in California"
5. "Find luxury rentals with at least 4 bedrooms"

What type of rental property are you looking for?
"""