"""
  venue.py
  
  Defines the Django model for a concert venue, including:
  name, city, and state
"""

from django.db import models


class Venue(models.Model):
    """Represents a concert venue in the database"""
    name = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
