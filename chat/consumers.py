import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Thread, Reply

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'forum'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']

        if message_type == 'new_thread':
            # In a real app, validate and save via view, but for demo, simulate
            # Here, we can broadcast directly, but better to use HTTP for persistence
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'new_thread_message',
                    'thread': text_data_json
                }
            )
        elif message_type == 'new_reply':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'new_reply_message',
                    'reply': text_data_json
                }
            )

    async def new_thread_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_thread',
            'thread': event['thread']
        }))

    async def new_reply_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_reply',
            'reply': event['reply']
        }))
