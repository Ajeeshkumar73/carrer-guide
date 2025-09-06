from django.db import models
from django.contrib.auth.models import User

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)   # who posted
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1–5 stars
    text = models.TextField()   # review message
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.rating}★"
