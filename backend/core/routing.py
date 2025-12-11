from django.urls import re_path
from . import consumers
from . import dm_consumer

# WebSocket URL patterns
websocket_urlpatterns = [
    # Group chat: ws://<host>/ws/group/<room_name>/?user=<username>
    re_path(r'ws/group/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
    
    # Direct message: ws://<host>/ws/dm/<recipient_username>/?user=<current_username>
    re_path(r'ws/dm/(?P<username>\w+)/$', dm_consumer.DirectMessageConsumer.as_asgi()),
]
