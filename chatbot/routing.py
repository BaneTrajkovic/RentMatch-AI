from django.urls import path

from . import consumers

# https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/function-calling/intro_function_calling.ipynb
websocket_urlpatterns = [
    path("ws/chatbot/new/", consumers.ChatConsumer.as_asgi()),
    path("ws/chatbot/<int:conversation_id>/", consumers.ChatConsumer.as_asgi()),
]