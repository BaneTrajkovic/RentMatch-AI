import json
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
from .models import Property, PropertyChat, PropertyChatMessage
from .helpers import generate_negotiation_response, should_ai_respond

class PropertyChatConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]
        
        # Check if the user is authenticated
        if not self.user.is_authenticated:
            self.close()
            return
        
        # Get the chat_id from the URL route
        self.chat_id = self.scope['url_route']['kwargs'].get('chat_id')
        self.chat_group_name = f'property_chat_{self.chat_id}'
        
        # Join the chat group
        async_to_sync(self.channel_layer.group_add)(
            self.chat_group_name,
            self.channel_name
        )
        
        # Accept the connection
        self.accept()
        
        # Fetch and send chat history if this is an existing chat
        if self.chat_id and self.chat_id != 'new':
            chat_history = self.get_chat_history(self.chat_id)
            self.send(text_data=json.dumps({
                'type': 'chat_history',
                'messages': chat_history
            }))

    def disconnect(self, close_code):
        # Leave the chat group
        async_to_sync(self.channel_layer.group_discard)(
            self.chat_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'message')
        
        if message_type == 'message':
            message = text_data_json['message']
            
            # Determine if this is a new chat or an existing one
            if self.chat_id == 'new':
                # Create a new chat
                property_id = text_data_json.get('property_id')
                
                # Handle auto-landlord case (direct application from property page)
                if text_data_json.get('auto_landlord', False):
                    try:
                        # Get the landlord with username "landlordMVP"
                        landlord = User.objects.get(username="landlordMVP")
                        landlord_id = landlord.id
                        renter_id = self.user.id
                    except User.DoesNotExist:
                        self.send(text_data=json.dumps({
                            'type': 'error',
                            'message': 'Default landlord "landlordMVP" not found'
                        }))
                        return
                else:
                    # Regular case with specified landlord/renter
                    landlord_id = text_data_json.get('landlord_id')
                    renter_id = text_data_json.get('renter_id')
                
                if not property_id:
                    self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': 'Missing property information'
                    }))
                    return
                
                # Create the chat
                chat = self.create_chat(property_id, landlord_id, renter_id)
                
                # Update the chat_id and group_name
                self.chat_id = chat['id']
                self.chat_group_name = f'property_chat_{self.chat_id}'
                
                # Join the new chat group
                async_to_sync(self.channel_layer.group_add)(
                    self.chat_group_name,
                    self.channel_name
                )
                
                # Save the initial message
                sender_type = 'landlord' if self.is_landlord(self.chat_id) else 'renter'
                saved_message = self.save_message(self.chat_id, self.user.id, message, sender_type)
                
                # Notify client about the new chat with the initial message
                self.send(text_data=json.dumps({
                    'type': 'chat_created',
                    'chat': chat,
                    'initial_message': saved_message
                }))
                
                # Send an AI welcome response if the message begins with "AI:"
                if should_ai_respond(message):
                    self.send_ai_response(message)
                
                return
                
            # For existing chats, save the message
            sender_type = 'landlord' if self.is_landlord(self.chat_id) else 'renter'
            saved_message = self.save_message(self.chat_id, self.user.id, message, sender_type)
            
            # Forward the message to the chat group
            async_to_sync(self.channel_layer.group_send)(
                self.chat_group_name,
                {
                    'type': 'chat_message',
                    'message': saved_message
                }
            )
            
            # Process AI response asynchronously without blocking further user messages
            # unless the message is explicitly directed at the AI
            if should_ai_respond(message):
                self.send_ai_response(message)

    def chat_message(self, event):
        message = event['message']
        
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message
        }))

    def get_chat_history(self, chat_id):
        try:
            chat = PropertyChat.objects.get(id=chat_id)
            messages = chat.messages.all()
            
            return [
                {
                    'id': msg.id,
                    'content': msg.content,
                    'sender_type': msg.sender_type,
                    'sender': msg.user.username if msg.user else 'AI Assistant',
                    'timestamp': msg.timestamp.isoformat()
                }
                for msg in messages
            ]
        except PropertyChat.DoesNotExist:
            return []

    def create_chat(self, property_id, landlord_id, renter_id):
        # Get property using zpid which is the primary key
        property_obj = Property.objects.get(zpid=property_id)
        landlord = User.objects.get(id=landlord_id)
        renter = User.objects.get(id=renter_id)
        
        chat = PropertyChat.objects.create(
            property=property_obj,
            landlord=landlord,
            renter=renter
        )
        
        return {
            'id': chat.id,
            'title': chat.title,
            'property': {
                'id': property_obj.zpid,
                'address': property_obj.address,
                'image_url': property_obj.main_image_url
            },
            'landlord': {
                'id': landlord.id,
                'username': landlord.username
            },
            'renter': {
                'id': renter.id,
                'username': renter.username
            },
            'created_at': chat.created_at.isoformat()
        }

    def save_message(self, chat_id, user_id, content, sender_type):
        chat = PropertyChat.objects.get(id=chat_id)
        user = User.objects.get(id=user_id) if user_id else None
        
        message = PropertyChatMessage.objects.create(
            chat=chat,
            user=user,
            content=content,
            sender_type=sender_type
        )
        
        return {
            'id': message.id,
            'content': message.content,
            'sender_type': message.sender_type,
            'sender': message.user.username if message.user else 'AI Assistant',
            'timestamp': message.timestamp.isoformat()
        }

    def is_landlord(self, chat_id):
        chat = PropertyChat.objects.get(id=chat_id)
        return self.user.id == chat.landlord.id
    
    def send_ai_response(self, user_message):
        """
        Generates and sends an AI response based on the user's message.
        
        Args:
            user_message: The message that triggered the AI response
        """
        try:
            # Get the chat
            chat = PropertyChat.objects.get(id=self.chat_id)
            
            # Generate AI response
            ai_response = generate_negotiation_response(chat, user_message)
            
            # If there's no response (e.g., message doesn't start with AI:), return
            if not ai_response:
                return
            
            # Save the AI response
            ai_message = self.save_message(self.chat_id, None, ai_response, 'bot')
            
            # Send the AI response to the chat group
            async_to_sync(self.channel_layer.group_send)(
                self.chat_group_name,
                {
                    'type': 'chat_message',
                    'message': ai_message
                }
            )
            
        except PropertyChat.DoesNotExist:
            # Handle case where chat doesn't exist
            self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Chat not found'
            }))
            
        except Exception as e:
            # Handle any other errors
            error_response = f"An error occurred with the AI assistant: {str(e)}"
            error_message = self.save_message(self.chat_id, None, error_response, 'bot')
            
            async_to_sync(self.channel_layer.group_send)(
                self.chat_group_name,
                {
                    'type': 'chat_message',
                    'message': error_message
                }
            )