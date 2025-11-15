from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from chat.models import Thread, Category

class ViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name='Test Category', description='Test description')

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_register_view(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_thread_creation_requires_login(self):
        response = self.client.post(reverse('create_thread'), {
            'title': 'Test Thread',
            'content': 'Test content',
            'category': self.category.id
        })
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_thread_creation_with_login(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('create_thread'), {
            'title': 'Test Thread',
            'content': 'Test content',
            'category': self.category.id
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Thread.objects.filter(title='Test Thread').exists())

    def test_search_view(self):
        Thread.objects.create(
            title='Search Test',
            content='Search content',
            author=self.user,
            category=self.category
        )
        response = self.client.get(reverse('search'), {'q': 'Search'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreater(len(data['threads']), 0)
