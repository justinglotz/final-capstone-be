"""
  venue.py
  
  Defines the Django model for a concert venue, including:
  name, city, and state
"""

from django.db import models


class Venue(models.Model):
    """Represents a concert venue in the database"""
    name = models.CharField(max_length=50)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    setlist_fm_id = models.CharField(
        max_length=50, unique=True, null=True, blank=True)
