"""
    follow.py

    Defines the Django model for a follow, including:
    follower (user who is following someone), and following (the user who is followed)
    """
from django.db import models
from .user import User


class Follow(models.Model):
    """Represents a follow in the database"""
    follower = models.ForeignKey(
        User, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(
        User, related_name='followers', on_delete=models.CASCADE)
