import json
import re
from channels.generic.websocket import WebsocketConsumer
from .models import ChatbotConversation, ChatbotMessage
from .helpers import get_chat_from_conversation, detect_profile_update_intent, send_message_with_function_calling

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
                    self.chat = get_chat_from_conversation(self.conversation)
                    self.accept()  # Accept the connection
    
                except ChatbotConversation.DoesNotExist:
                    
                    self.close()
                    return
            else:
    
                self.close()
    
        else:
    
            self.close()

    
    def receive(self, text_data=None, bytes_data=None):

        user_message = json.loads(text_data)["message"]
        
        # Check if message is related to profile updating
        profile_update_intent = detect_profile_update_intent(user_message)
        
        # Create a new conversation on first message if needed
        if self.conversation is None:
            self.conversation = ChatbotConversation.objects.create(user=self.scope["user"])
            self.chat = get_chat_from_conversation(self.conversation)
            
        # Save user message to database
        ChatbotMessage.objects.create(
            conversation=self.conversation,
            role='user',
            content=user_message
        )
        
        # If user wants to update profile, provide direct guidance before AI response
        if profile_update_intent:
            profile_message = (
                "I see you want to update your profile information. "
                "You can update your profile by [visiting your profile page](/users/profile/edit/). "
                "Your profile information helps us generate accurate lease documents and personalize your experience."
            )
            
            # Save bot response for profile update
            ChatbotMessage.objects.create(
                conversation=self.conversation,
                role='model',
                content=profile_message
            )
            
            # Send direct response to client
            self.send(text_data=json.dumps({
                "type": "chat_message",
                "message": profile_message
            }))
            return
        
        # Send to AI and get response for normal messages
        response_text = send_message_with_function_calling(self.chat, user_message)
                
        # Update title for new conversations
        if self.conversation.title == "New Conversation" and len(self.chat.get_history()) // 2 > 3:
            title_response = self.chat.send_message(CONVERSATION_TITLE)
            self.conversation.title = title_response.text[:50]
            self.conversation.save()
            
            self.send(text_data=json.dumps({
                "type": "conversation_created",
                "conversation_id": self.conversation.id,
                "title": self.conversation.title
            }))
        
        # Save bot response
        ChatbotMessage.objects.create(
            conversation=self.conversation,
            role='model',
            content=response_text
        )
        
        # Send response to client
        self.send(text_data=json.dumps({
            "type": "chat_message",
            "message": response_text
        }))