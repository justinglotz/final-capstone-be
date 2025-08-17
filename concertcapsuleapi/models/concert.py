"""
    concert.py

    Defines the Django model for a concert, including:
    artist id, venue id, tour name, date and time
    """
from django.db import models
from .artist import Artist
from .venue import Venue


class Concert(models.Model):
    """Represents a concert in the database"""
    artist = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True)
    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True)
    tour_name = models.CharField(max_length=50)
    date = models.DateField()
    time = models.TimeField()
