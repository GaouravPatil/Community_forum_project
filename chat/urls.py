from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),                  # main landing page
    path('chat/', views.home, name='chat_home'),         # internal forum home
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),  # Ensure this exists

    # notifications
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/mark-read/<int:notif_id>/', views.mark_notification_read, name='mark_notification_read'),

    # calls (REST endpoints)
    path('call/initiate/', views.initiate_call, name='initiate_call'),
    path('call/accept/<int:call_id>/', views.accept_call, name='accept_call'),
    path('call/reject/<int:call_id>/', views.reject_call, name='reject_call'),
    path('call/end/<int:call_id>/', views.end_call, name='end_call'),
    path('call/page/<int:call_id>/', views.call_page, name='call_page'),

    # simple helpers
    path('search/', views.search, name='search'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]
