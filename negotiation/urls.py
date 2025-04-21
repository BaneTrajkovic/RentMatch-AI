from django.urls import path
from . import views

app_name = 'negotiation'

urlpatterns = [
    path('chats/', views.ChatListView.as_view(), name='chat_list'),
    path('chat/<int:chat_id>/', views.ChatDetailView.as_view(), name='chat_detail'),
    path('chat/new/', views.NewChatView.as_view(), name='new_chat'),
    path('properties/', views.PropertyListView.as_view(), name='property_list'),
]