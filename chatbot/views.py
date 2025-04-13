from typing import Any
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.views.generic import DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import ChatbotConversation
from django.http import Http404

# Create your views here.
class ChatbotView(LoginRequiredMixin, DetailView):
    model = ChatbotConversation
    template_name = "chatbot/chat.html"
    context_object_name = "conversation"

    def get_object(self, queryset=None):

        if queryset is None:
            queryset = self.get_queryset()
            
        conversation = super().get_object(queryset=queryset)
        
        # Only allowing the user who owns the conversation to actually see the conversation
        if conversation.user != self.request.user:
            raise Http404("Conversation not found")
        
        return conversation

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add user's conversations to context
        context['user_conversations'] = ChatbotConversation.objects.filter(user=self.request.user) # Most recent first
        
        return context
    

class NewChatbotView(LoginRequiredMixin, TemplateView):
    template_name = "chatbot/chat.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add user's conversations to context
        context['user_conversations'] = ChatbotConversation.objects.filter(user=self.request.user) # Most recent first
    
        return context





