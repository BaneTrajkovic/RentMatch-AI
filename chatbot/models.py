from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ChatbotConversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chatbot_conversations')
    title = models.CharField(max_length=255, default="New Conversation")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"

class ChatbotMessage(models.Model):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('model', 'Model'),
    )
    
    conversation = models.ForeignKey(ChatbotConversation, on_delete=models.CASCADE, related_name='chatbot_messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    
    # specifies default ordering for queries on the model
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"Role {self.role}: {self.content[:50]}"