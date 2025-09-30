from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create-thread/', views.create_thread, name='create_thread'),
    path('create-reply/<int:thread_id>/', views.create_reply, name='create_reply'),
]
