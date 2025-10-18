from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('assistant-login/', views.login_assistant, name='login_assistant'),  # <-- make sure name exists
    path("predicts/", views.predict_page, name="predict_page"),
    path("assistant/", views.assistant, name="assistant"),
    path("sign/", views.log, name="log"),
     path("predict/", views.predict_career, name="predict_career"),


    
]
