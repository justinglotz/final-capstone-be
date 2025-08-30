from django.http import HttpResponseServerError
from rest_framework.response import Response
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from concertcapsuleapi.models import Concert, Artist, Venue, UserConcert, User


class ConcertView(viewsets.ViewSet):
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
            tour_name=request.data.get("tourName"),
            date=request.data["date"],
            time=request.data.get("time")
        )
        fb_uid = request.data.get("uid_firebase")
        user = User.objects.get(uid_firebase=fb_uid)

        UserConcert.objects.create(
            concert=concert,
            user=user,
        )
        serializer = ConcertSerializer(concert)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        """Handle GET requests to get all concerts by username"""
        username = request.query_params.get("username")
        user = User.objects.get(username=username)
        concerts = Concert.objects.filter(
            userconcerts__user=user).order_by('-date')
        serializer = ConcertSerializer(concerts, many=True)
        return Response(serializer.data)

    def destroy(self, request, pk):
        """Handle DELETE requests for concerts"""
        # Delete the row in the userConcert table where the concert_id and user_id match
        concert_id = pk
        username = request.query_params.get("username")
        user = User.objects.get(username=username)
        user_concert = UserConcert.objects.get(
            concert_id=concert_id,
            user_id=user
        )
        user_concert.delete()
        return Response({"Concert successfully deleted"}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_path='add-to-profile', url_name='add-to-profile')
    def add_to_profile(self, request, pk=None):
        concert_id = pk
        username = request.data.get('username')
        user = User.objects.get(username=username)
        user_concert, created = UserConcert.objects.get_or_create(
            concert_id=concert_id,
            user=user
        )
        if created:
            return Response({'message': 'Concert added to profile'}, status=201)
        else:
            return Response({'message': 'Concert already in profile'}, status=200)


class ConcertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concert
        fields = ('id', 'artist', 'venue', 'tour_name', 'date', 'time')
        depth = 1
