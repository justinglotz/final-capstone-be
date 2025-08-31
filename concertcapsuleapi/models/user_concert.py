"""
    user_concert.py

    Defines the Django model to represent a user attending a concert (AKA creating a "ticket")
    """
from django.db import models
from .user import User
from .concert import Concert


class UserConcert(models.Model):
    """Represents an instance of a user attending a concert, AKA a ticket"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    concert = models.ForeignKey(
        Concert, on_delete=models.CASCADE, related_name="userconcerts")
    created_at = models.DateTimeField(auto_now_add=True)
