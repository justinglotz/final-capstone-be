from django.http import HttpResponseServerError
from rest_framework.response import Response
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from concertcapsuleapi.models import Concert, Artist, Venue, UserConcert, User, Like
from concertcapsuleapi.serializers import ConcertSerializer, UserConcertSerializer
from firebase_admin import auth


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
        """Handle GET requests to get all concerts (userConcert objects) by username"""
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            firebase_token = auth_header.split(' ')[1]
            decoded_token = auth.verify_id_token(
                firebase_token, clock_skew_seconds=5)
            firebase_uid = decoded_token['uid']
            current_user = User.objects.filter(
                uid_firebase=firebase_uid).first()
        username = request.query_params.get("username")
        user = User.objects.get(username=username)
        user_concerts = UserConcert.objects.filter(
            user=user).order_by("-concert__date")

        serializer = UserConcertSerializer(
            user_concerts, many=True, context={'user': current_user})
        return Response(serializer.data)

    def destroy(self, pk):
        """Handle DELETE requests for concerts"""
        # Delete the row in the userConcert table where the concert_id and user_id match
        user_concert = UserConcert.objects.get(
            pk=pk
        )
        user_concert.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_path='add-to-profile', url_name='add-to-profile')
    def add_to_profile(self, request, pk=None):
        concert_id = pk
        username = request.data.get('username')
        user = User.objects.get(username=username)
        concert = Concert.objects.get(id=concert_id)
        existing = UserConcert.objects.filter(concert=concert, user=user)
        user_concert, created = UserConcert.objects.get_or_create(
            concert=concert,
            user=user
        )
        if created:
            return Response({'message': 'Concert added to profile'}, status=201)
        else:
            return Response({'message': 'Concert already in profile'}, status=200)

    @action(detail=True, methods=['get'])
    def get_likes(self, request, pk=None):
        user_concert_id = pk
        likes = Like.objects.filter(
            user_concert_id=user_concert_id).select_related('user')
        usernames = [like.user.username for like in likes]
        return Response({'usernames': usernames}, status=200)

    @action(detail=False, methods=['post'])
    def pin_concert(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            firebase_token = auth_header.split(' ')[1]
            decoded_token = auth.verify_id_token(
                firebase_token, clock_skew_seconds=5)
            firebase_uid = decoded_token['uid']
            current_user = User.objects.filter(
                uid_firebase=firebase_uid).first()
            user_concert_id = request.data.get('user_concert')
        try:
            user_concert = UserConcert.objects.get(
                id=user_concert_id,
                user=current_user
            )
            user_concert.pinned = True
            user_concert.save()
            return Response({'Concert pinned to profile'}, status=200)
        except UserConcert.DoesNotExist:
            return Response({'error': 'Not authorized or ticket not found'}, status=403)

    @action(detail=False, methods=['delete'])
    def unpin_concert(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            firebase_token = auth_header.split(' ')[1]
            decoded_token = auth.verify_id_token(
                firebase_token, clock_skew_seconds=5)
            firebase_uid = decoded_token['uid']
            current_user = User.objects.filter(
                uid_firebase=firebase_uid).first()
            user_concert_id = request.data.get('user_concert')
        try:
            user_concert = UserConcert.objects.get(
                id=user_concert_id,
                user=current_user
            )
            user_concert.pinned = False
            user_concert.save()
            return Response({'Concert unpinned from profile'}, status=200)
        except UserConcert.DoesNotExist:
            return Response({'error': 'Not authorized or ticket not found'}, status=403)
