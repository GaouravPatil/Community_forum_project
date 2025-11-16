from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/?$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/video-call/(?P<call_id>\d+)/?$', consumers.VideoCallConsumer.as_asgi()),
<<<<<<< HEAD
    re_path(r'ws/group-call/(?P<room_id>[a-zA-Z0-9_-]+)/?$', consumers.GroupVideoCallConsumer.as_asgi()),
=======
    re_path(r'ws/group-call/(?P<room_id>[-\w]+)/?$', consumers.GroupVideoCallConsumer.as_asgi()),
>>>>>>> 0fdd7e8 (Refurbished)
]
