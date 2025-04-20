from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Property, PropertyChat, PropertyChatMessage

class ChatListView(LoginRequiredMixin, ListView):
    """View for displaying all chats for the current user"""
    model = PropertyChat
    template_name = 'negotiation/chat_list.html'
    context_object_name = 'chats'
    
    def get_queryset(self):
        # Get chats where the user is either landlord or renter
        return PropertyChat.objects.filter(
            landlord=self.request.user
        ).union(
            PropertyChat.objects.filter(renter=self.request.user)
        ).order_by('-updated_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add user's chats for the sidebar
        context['user_chats'] = self.get_queryset()
        return context

class ChatDetailView(LoginRequiredMixin, DetailView):
    """View for displaying a specific chat and its messages"""
    model = PropertyChat
    template_name = 'negotiation/chat_detail.html'
    context_object_name = 'chat'
    pk_url_kwarg = 'chat_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add messages to context
        context['messages'] = self.object.messages.all().order_by('timestamp')
        # Determine if user is landlord or renter
        context['is_landlord'] = (self.request.user == self.object.landlord)
        # Add chat_id for active highlighting in sidebar
        context['chat_id'] = self.object.id
        # Add user's chats for the sidebar
        context['user_chats'] = PropertyChat.objects.filter(
            landlord=self.request.user
        ).union(
            PropertyChat.objects.filter(renter=self.request.user)
        ).order_by('-updated_at')
        return context
    
    def get_object(self, queryset=None):
        # Get the chat and ensure the user is either the landlord or renter
        obj = get_object_or_404(PropertyChat, pk=self.kwargs['chat_id'])
        if self.request.user != obj.landlord and self.request.user != obj.renter:
            # User not authorized for this chat
            return redirect('negotiation:chat_list')
        return obj

class NewChatView(LoginRequiredMixin, TemplateView):
    """View for creating a new chat"""
    template_name = 'negotiation/new_chat.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add available properties to context
        if self.request.user.is_staff:
            # If user is staff/admin, show properties where they're the landlord
            context['properties'] = Property.objects.all()
            context['is_landlord'] = True
            # Get available renters
            context['users'] = User.objects.exclude(id=self.request.user.id)
        else:
            # If regular user, show properties they can rent
            context['properties'] = Property.objects.all()  # In a real app, filter by availability
            context['is_landlord'] = False
            # Get available landlords
            context['users'] = User.objects.filter(is_staff=True)
        
        # Add user's chats for the sidebar
        context['user_chats'] = PropertyChat.objects.filter(
            landlord=self.request.user
        ).union(
            PropertyChat.objects.filter(renter=self.request.user)
        ).order_by('-updated_at')
        
        return context

class PropertyListView(LoginRequiredMixin, ListView):
    """View for displaying all properties"""
    model = Property
    template_name = 'negotiation/property_list.html'
    context_object_name = 'properties'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add user's chats for the sidebar
        context['user_chats'] = PropertyChat.objects.filter(
            landlord=self.request.user
        ).union(
            PropertyChat.objects.filter(renter=self.request.user)
        ).order_by('-updated_at')
        return context