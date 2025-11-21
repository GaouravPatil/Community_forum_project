from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create-thread/', views.create_thread, name='create_thread'),
    path('create-reply/<int:thread_id>/', views.create_reply, name='create_reply'),
    path('register/', views.register, name='register'),
    path('vote/<str:model_type>/<int:object_id>/', views.vote, name='vote'),
    path('send-chat-message/', views.send_chat_message, name='send_chat_message'),
    path('profile/', views.profile, name='profile'),
    path('notifications/', views.notifications, name='notifications'),
    path('search/', views.search, name='search'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('category/<int:pk>/', views.category_detail, name='category_detail'),
    path('create-thread-page/', views.create_thread_page, name='create_thread_page'),

    



    
    
]


