import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.auth import get_user
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from .models import (
    Thread, Reply, Vote, ChatMessage,
    VideoCall, GroupVideoCall, Category, Notification
)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'forum'
        self.user = await get_user(self.scope)

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
            if not self.user.is_authenticated:
                await self.send(text_data=json.dumps({'error': 'Authentication required'}))
                return
            title = text_data_json.get('title')
            content = text_data_json.get('content')
            category_id = text_data_json.get('category_id')
            if title and content:
                thread = await self.create_thread(title, content, category_id, self.user)
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
                                'category': thread.category.name if thread.category else 'General',
                                'created_at': str(thread.created_at),
                            }
                        }
                    )
            else:
                await self.send(text_data=json.dumps({'error': 'Invalid thread data'}))

        elif message_type == 'new_reply':
            if not self.user.is_authenticated:
                await self.send(text_data=json.dumps({'error': 'Authentication required'}))
                return
            thread_id = text_data_json.get('thread_id')
            content = text_data_json.get('content')
            if thread_id and content:
                reply = await self.create_reply(thread_id, content, self.user)
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

        elif message_type == 'vote':
            if not self.user.is_authenticated:
                await self.send(text_data=json.dumps({'error': 'Authentication required'}))
                return
            model_type = text_data_json.get('model_type')
            object_id = text_data_json.get('object_id')
            vote_type = text_data_json.get('vote_type')
            if model_type and object_id is not None and vote_type in [1, -1]:
                updated_vote = await self.handle_vote(model_type, object_id, vote_type, self.user)
                if updated_vote:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'vote_update_message',
                            'vote': {
                                'model_type': model_type,
                                'object_id': object_id,
                                'vote_count': updated_vote['vote_count'],
                                'user_vote': updated_vote['user_vote'],
                            }
                        }
                    )
            else:
                await self.send(text_data=json.dumps({'error': 'Invalid vote data'}))

        elif message_type == 'chat_message':
            if not self.user.is_authenticated:
                await self.send(text_data=json.dumps({'error': 'Authentication required'}))
                return
            content = text_data_json.get('content')
            if content:
                message = await self.create_chat_message(content, self.user)
                if message:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message_broadcast',
                            'message': {
                                'id': message['id'],
                                'content': message['content'],
                                'author': message['author'],
                                'created_at': message['created_at'],
                            }
                        }
                    )
            else:
                await self.send(text_data=json.dumps({'error': 'Content is required'}))

    @database_sync_to_async
    def create_thread(self, title, content, category_id, user):
        try:
            category = None
            if category_id:
                category = Category.objects.get(id=category_id)
            thread = Thread.objects.create(title=title, content=content, author=user, category=category)
            return thread
        except Exception as e:
            print(f"Error creating thread: {e}")
            return None

    @database_sync_to_async
    def create_reply(self, thread_id, content, user):
        try:
            thread = Thread.objects.get(id=thread_id)
            reply = Reply.objects.create(thread=thread, content=content, author=user)

            # Create notification for thread author if not the same user
            if thread.author != user:
                Notification.objects.create(
                    user=thread.author,
                    message=f"{user.username} replied to your thread '{thread.title}'",
                    thread=thread,
                    reply=reply
                )

            return reply
        except Thread.DoesNotExist:
            return None
        except Exception as e:
            print(f"Error creating reply: {e}")
            return None

    @database_sync_to_async
    def handle_vote(self, model_type, object_id, vote_type, user):
        try:
            if model_type == 'thread':
                content_type = ContentType.objects.get_for_model(Thread)
                obj = Thread.objects.get(id=object_id)
            elif model_type == 'reply':
                content_type = ContentType.objects.get_for_model(Reply)
                obj = Reply.objects.get(id=object_id)
            else:
                return None

            vote_obj, created = Vote.objects.get_or_create(
                content_type=content_type,
                object_id=object_id,
                user=user,
                defaults={'vote_type': vote_type}
            )

            if not created:
                if vote_obj.vote_type == vote_type:
                    vote_obj.delete()
                else:
                    vote_obj.vote_type = vote_type
                    vote_obj.save()

            return {'vote_count': obj.vote_count(), 'user_vote': obj.user_vote(user)}
        except Exception as e:
            print(f"Error handling vote: {e}")
            return None

    @database_sync_to_async
    def create_chat_message(self, content, user):
        try:
            message = ChatMessage.objects.create(content=content, author=user)
            return {
                'id': message.id,
                'content': message.content,
                'author': message.author.username,
                'created_at': message.created_at.isoformat(),
            }
        except Exception as e:
            print(f"Error creating chat message: {e}")
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

    async def vote_update_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'vote_update',
            'vote': event['vote']
        }))

    async def chat_message_broadcast(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_chat_message',
            'message': event['message']
        }))

    async def notification_broadcast(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'notification': event['notification']
        }))


class VideoCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = await get_user(self.scope)
        self.call_id = self.scope['url_route']['kwargs'].get('call_id')
        self.room_group_name = f'video_call_{self.call_id}'

        if not self.user.is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Notify others that user joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'username': self.user.username,
                'user_id': self.user.id,
            }
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'username': self.user.username,
                'user_id': self.user.id,
            }
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'offer':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'offer_message',
                    'from_user': self.user.id,
                    'offer': data.get('offer'),
                }
            )
        elif message_type == 'answer':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'answer_message',
                    'from_user': self.user.id,
                    'answer': data.get('answer'),
                }
            )
        elif message_type == 'ice_candidate':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'ice_candidate_message',
                    'from_user': self.user.id,
                    'candidate': data.get('candidate'),
                }
            )
        elif message_type == 'call_end':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'call_ended',
                    'from_user': self.user.id,
                }
            )
            await self.end_video_call()
        elif message_type == 'call_reject':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'call_rejected',
                    'from_user': self.user.id,
                }
            )
            await self.reject_video_call()
        elif message_type == 'call_accept':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'call_accepted',
                    'from_user': self.user.id,
                }
            )
            await self.accept_video_call()

    async def user_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'username': event['username'],
            'user_id': event['user_id'],
        }))

    async def user_left(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'username': event['username'],
            'user_id': event['user_id'],
        }))

    async def offer_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'offer',
            'from_user': event['from_user'],
            'offer': event['offer'],
        }))

    async def answer_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'answer',
            'from_user': event['from_user'],
            'answer': event['answer'],
        }))

    async def ice_candidate_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'ice_candidate',
            'from_user': event['from_user'],
            'candidate': event['candidate'],
        }))

    async def call_ended(self, event):
        await self.send(text_data=json.dumps({
            'type': 'call_ended',
            'from_user': event['from_user'],
        }))

    async def call_rejected(self, event):
        await self.send(text_data=json.dumps({
            'type': 'call_rejected',
            'from_user': event['from_user'],
        }))

    async def call_accepted(self, event):
        await self.send(text_data=json.dumps({
            'type': 'call_accepted',
            'from_user': event['from_user'],
        }))

    @database_sync_to_async
    def end_video_call(self):
        try:
            call = VideoCall.objects.get(id=self.call_id)
            call.status = 'ended'
            call.end_time = timezone.now()
            call.save()
        except VideoCall.DoesNotExist:
            pass

    @database_sync_to_async
    def reject_video_call(self):
        try:
            call = VideoCall.objects.get(id=self.call_id)
            call.status = 'rejected'
            call.save()
        except VideoCall.DoesNotExist:
            pass

    @database_sync_to_async
    def accept_video_call(self):
        try:
            call = VideoCall.objects.get(id=self.call_id)
            call.status = 'accepted'
            call.save()
        except VideoCall.DoesNotExist:
            pass


class GroupVideoCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = await get_user(self.scope)
        self.room_id = self.scope['url_route']['kwargs'].get('room_id')
        self.room_group_name = f'group_video_call_{self.room_id}'

        if not self.user.is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined_group',
                'username': self.user.username,
                'user_id': self.user.id,
            }
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left_group',
                'username': self.user.username,
                'user_id': self.user.id,
            }
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'offer':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'group_offer',
                    'from_user': self.user.id,
                    'to_user': data.get('to_user'),
                    'offer': data.get('offer'),
                }
            )
        elif message_type == 'answer':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'group_answer',
                    'from_user': self.user.id,
                    'to_user': data.get('to_user'),
                    'answer': data.get('answer'),
                }
            )
        elif message_type == 'ice_candidate':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'group_ice_candidate',
                    'from_user': self.user.id,
                    'to_user': data.get('to_user'),
                    'candidate': data.get('candidate'),
                }
            )

    async def user_joined_group(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'username': event['username'],
            'user_id': event['user_id'],
        }))

    async def user_left_group(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'username': event['username'],
            'user_id': event['user_id'],
        }))

    async def group_offer(self, event):
        if event['to_user'] == self.user.id or event['to_user'] is None:
            await self.send(text_data=json.dumps({
                'type': 'offer',
                'from_user': event['from_user'],
                'offer': event['offer'],
            }))

    async def group_answer(self, event):
        if event['to_user'] == self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'answer',
                'from_user': event['from_user'],
                'answer': event['answer'],
            }))

    async def group_ice_candidate(self, event):
        if event['to_user'] == self.user.id or event['to_user'] is None:
            await self.send(text_data=json.dumps({
                'type': 'ice_candidate',
                'from_user': event['from_user'],
                'candidate': event['candidate'],
            }))
