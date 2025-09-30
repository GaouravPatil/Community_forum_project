import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Thread, Reply
from django.contrib.auth.models import User

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
        message_type = text_data_json.get('type')

        if message_type == 'new_thread':
            title = text_data_json.get('title')
            content = text_data_json.get('content')
            user_id = text_data_json.get('user_id')
            if title and content and user_id:
                thread = await self.create_thread(title, content, user_id)
                if thread:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'new_thread_message',
                            'thread': {
                                'id': thread.id,
                                'title': thread.title,
                                'content': thread.content,
                                'author': thread.author.username,
                                'created_at': str(thread.created_at),
                            }
                        }
                    )
            else:
                await self.send(text_data=json.dumps({'error': 'Invalid thread data'}))

        elif message_type == 'new_reply':
            thread_id = text_data_json.get('thread_id')
            content = text_data_json.get('content')
            user_id = text_data_json.get('user_id')
            if thread_id and content and user_id:
                reply = await self.create_reply(thread_id, content, user_id)
                if reply:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'new_reply_message',
                            'reply': {
                                'id': reply.id,
                                'content': reply.content,
                                'thread_id': reply.thread.id,
                                'author': reply.author.username,
                                'created_at': str(reply.created_at),
                            }
                        }
                    )
            else:
                await self.send(text_data=json.dumps({'error': 'Invalid reply data'}))

    @database_sync_to_async
    def create_thread(self, title, content, user_id):
        try:
            user = User.objects.get(id=user_id)
            thread = Thread.objects.create(title=title, content=content, author=user)
            return thread
        except User.DoesNotExist:
            return None
        except Exception as e:
            print(f"Error creating thread: {e}")
            return None

    @database_sync_to_async
    def create_reply(self, thread_id, content, user_id):
        try:
            user = User.objects.get(id=user_id)
            thread = Thread.objects.get(id=thread_id)
            reply = Reply.objects.create(thread=thread, content=content, author=user)
            return reply
        except (User.DoesNotExist, Thread.DoesNotExist):
            return None
        except Exception as e:
            print(f"Error creating reply: {e}")
            return None

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
