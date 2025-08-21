from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from concertcapsuleapi.models import Concert, Artist, Venue


class ConcertView(ViewSet):
    def create(self, request):
        """Handle POST requests to create a new concert"""
        artist, created = Artist.objects.get_or_create(
            spotify_id=request.data["artist"]["id"],
            defaults={
                'name': request.data["artist"]["name"]
            }
        )
        venue, created = Venue.objects.get_or_create(
            setlist_fm_id=request.data["venue"]["setlist_fm_id"],
            defaults={
                'name': request.data["venue"]["name"],
                'city': request.data["venue"]["city"],
                'state': request.data["venue"]["state"]
            }
        )
        concert = Concert.objects.create(
            artist=artist,
            venue=venue,
            tour_name=request.data["tourName"],
            date=request.data["date"],
            time=request.data["time"]
        )
        serializer = ConcertSerializer(concert)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ConcertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concert
        fields = ('id', 'artist', 'venue', 'tour_name', 'date', 'time')
