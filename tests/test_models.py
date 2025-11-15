from django.test import TestCase
from django.contrib.auth.models import User
from chat.models import Thread, Reply, Category, Vote, ChatMessage, UserProfile, Notification

class ModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name='Test Category', description='Test description')
        self.thread = Thread.objects.create(
            title='Test Thread',
            content='Test content',
            author=self.user,
            category=self.category
        )

    def test_thread_creation(self):
        self.assertEqual(self.thread.title, 'Test Thread')
        self.assertEqual(self.thread.author, self.user)
        self.assertEqual(self.thread.category, self.category)

    def test_reply_creation(self):
        reply = Reply.objects.create(
            content='Test reply',
            thread=self.thread,
            author=self.user
        )
        self.assertEqual(reply.content, 'Test reply')
        self.assertEqual(reply.thread, self.thread)
        self.assertEqual(reply.author, self.user)

    def test_vote_creation(self):
        vote = Vote.objects.create(
            content_object=self.thread,
            user=self.user,
            vote_type=Vote.UPVOTE
        )
        self.assertEqual(vote.vote_type, Vote.UPVOTE)
        self.assertEqual(vote.user, self.user)

    def test_chat_message_creation(self):
        message = ChatMessage.objects.create(
            content='Test message',
            author=self.user
        )
        self.assertEqual(message.content, 'Test message')
        self.assertEqual(message.author, self.user)

    def test_user_profile_creation(self):
        profile = UserProfile.objects.create(user=self.user)
        self.assertEqual(profile.user, self.user)

    def test_notification_creation(self):
        notification = Notification.objects.create(
            user=self.user,
            message='Test notification',
            thread=self.thread
        )
        self.assertEqual(notification.message, 'Test notification')
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.thread, self.thread)
