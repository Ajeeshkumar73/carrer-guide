from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('userpage/', views.userpage_view, name='userpage'),
    path("submit-review/", views.submit_review, name="submit_review"),
    path("user_page/", views.user_page, name="user_page"),
    path("predict/", views.predict_page, name="predict_page"),
    path("assistant/", views.assistant, name="assistant"),

    
]
