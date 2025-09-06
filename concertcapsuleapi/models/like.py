"""
    like.py

    Defines the Django model for a like, including:
    ticket (the specific userConcert instance being liked), and user (the user who is doing the liking)
    """
from django.db import models
from .user_concert import UserConcert
from .user import User


class Like(models.Model):
    """Represents a like in the database"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE)
    user_concert = models.ForeignKey(
        UserConcert, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'user_concert')
