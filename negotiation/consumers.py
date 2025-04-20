import json
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
from .models import Property, PropertyChat, PropertyChatMessage

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
                landlord_id = text_data_json.get('landlord_id')
                renter_id = text_data_json.get('renter_id')
                
                if not all([property_id, landlord_id, renter_id]):
                    self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': 'Missing required information to create chat'
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
                
                # Notify client about the new chat
                self.send(text_data=json.dumps({
                    'type': 'chat_created',
                    'chat': chat
                }))
            
            # Save the message
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
            
            # Generate AI response
            ai_response = self.generate_ai_response(self.chat_id, message)
            
            # Save and send AI response
            ai_message = self.save_message(self.chat_id, None, ai_response, 'bot')
            async_to_sync(self.channel_layer.group_send)(
                self.chat_group_name,
                {
                    'type': 'chat_message',
                    'message': ai_message
                }
            )

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
        property_obj = Property.objects.get(id=property_id)
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
                'id': property_obj.id,
                'title': property_obj.title
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

    def generate_ai_response(self, chat_id, user_message):
        # Here you would integrate with the Gemini API
        # For now, we'll return a placeholder response
        
        # In the future, implement:
        # 1. Retrieve chat history for context
        # 2. Call Gemini API with appropriate instructions
        # 3. Process and return the AI response
        
        # Placeholder response
        return f"This is where the Gemini API would process: '{user_message}' and provide negotiation assistance. We'll implement this integration in the next step."