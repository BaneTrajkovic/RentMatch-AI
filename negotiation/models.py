from django.db import models
from django.contrib.auth.models import User

class Property(models.Model):
    """Simple Property model (placeholder for now)"""
    title = models.CharField(max_length=200)
    address = models.TextField()
    
    def __str__(self):
        return self.title

class PropertyChat(models.Model):
    """Chat between landlord and renter about a specific property"""
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='chats')
    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='landlord_chats')
    renter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='renter_chats')
    title = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Chat about {self.property.title} between {self.landlord.username} and {self.renter.username}"
    
    def save(self, *args, **kwargs):
        # Auto-generate title if not provided
        if not self.title:
            self.title = f"Discussion about {self.property.title}"
        super().save(*args, **kwargs)

class PropertyChatMessage(models.Model):
    """Individual message in a property chat"""
    SENDER_TYPES = [
        ('landlord', 'Landlord'),
        ('renter', 'Renter'),
        ('bot', 'AI Assistant')
    ]
    
    chat = models.ForeignKey(PropertyChat, on_delete=models.CASCADE, related_name='messages')
    sender_type = models.CharField(max_length=10, choices=SENDER_TYPES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='property_chat_messages', null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        if self.sender_type == 'bot':
            sender = 'AI Assistant'
        else:
            sender = self.user.username if self.user else 'Unknown'
        return f"{sender} in {self.chat}"