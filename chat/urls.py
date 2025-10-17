from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create-thread/', views.create_thread, name='create_thread'),
    path('create-reply/<int:thread_id>/', views.create_reply, name='create_reply'),
    path('register/', views.register, name='register'),
    path('vote/<str:model_type>/<int:object_id>/', views.vote, name='vote'),
    path('send-chat-message/', views.send_chat_message, name='send_chat_message'),
]
