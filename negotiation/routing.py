from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/property_chat/(?P<chat_id>\w+)/$', consumers.PropertyChatConsumer.as_asgi()),
]