import json
from channels.generic.websocket import WebsocketConsumer
from .models import ChatbotConversation, ChatbotMessage
from .helpers import get_chat_from_conversation

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
        
        # Send to AI and get response
        response = self.chat.send_message(user_message)
        response_text = response.text
        
        # Update title for new conversations
        if self.conversation.title == "New Conversation":
            title_response = self.chat.send_message("Based on my initial inquiry, suggest a short, descriptive title for this conversation (respond with just the title, no explanations, maximum 40 characters and forget that I ever asked you this message)")
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