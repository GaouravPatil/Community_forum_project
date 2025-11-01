from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create-thread/', views.create_thread, name='create_thread'),
    path('create-thread-form/', views.create_thread_form, name='create_thread_form'),
    path('create-reply/<int:thread_id>/', views.create_reply, name='create_reply'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('vote/<str:model_type>/<int:object_id>/', views.vote, name='vote'),
    path('send-chat-message/', views.send_chat_message, name='send_chat_message'),
    path('profile/', views.profile, name='profile'),
    path('notifications/', views.notifications, name='notifications'),
    path('search/', views.search, name='search'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

]
