# assistant_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('chat/', views.chat_api, name='chat_api'), # Endpoint for AJAX calls
]