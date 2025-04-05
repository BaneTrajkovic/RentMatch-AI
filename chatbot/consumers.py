import json
from google import genai
import constants

from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import User

class ChatConsumer(WebsocketConsumer):

    chat_sessions = {}
    
    def connect(self):
        self.user : User = self.scope["user"] 
        
        # Check if user is authenticated
        if self.user.is_authenticated:
            
            user_id = self.user.id

            # If not yet created chat session
            if self.user.id not in self.chat_sessions:

                # Create client
                client = genai.Client(api_key=constants.GEMINI_API_KEY)
                
                # Add user chat to chat sessions
                self.chat_sessions[user_id] = client.chats.create(model="gemini-2.0-flash")

            # Setup current user chat
            self.chat = self.chat_sessions[user_id]
            self.chat.send_message("""
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
""")
            
            self.accept()
        
        else:
        
            self.close()

    def disconnect(self, code):
        return super().disconnect(code)
    
    def receive(self, text_data=None, bytes_data=None):

        # here self.chat responds
        print(text_data)
        user_input_dict = json.loads(text_data)

        response = self.chat.send_message(user_input_dict["message"])

        self.send(text_data=json.dumps({"message" : response.text}))