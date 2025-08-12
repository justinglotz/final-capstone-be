"""
  artist.py
  
  Defines the Django model for a musical artist, including:
  Spotify ID, name, and any associated genres
"""

from django.db import models


class Artist(models.Model):
    """Represents a musical artist in the database"""
    spotify_id = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    genres = models.JSONField(default=list)
