from django.urls import re_path
from . import consumers, video_consumers

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/?$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/video-call/(?P<call_id>\d+)/?$', video_consumers.VideoCallConsumer.as_asgi()),
    re_path(r'ws/group-call/(?P<room_id>[a-zA-Z0-9_-]+)/?$', video_consumers.GroupVideoCallConsumer.as_asgi()),
]
