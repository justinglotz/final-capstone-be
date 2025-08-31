from django.http import HttpResponseServerError
from rest_framework.response import Response
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from concertcapsuleapi.models import Concert, Artist, Venue, UserConcert, User, Follow
from firebase_admin import auth


class FollowView(viewsets.ViewSet):
    def create(self, request):
        """Handle POST requests to add a follow"""
        firebase_token = request.data.get('firebase_token')
        decoded_token = auth.verify_id_token(firebase_token)
        firebase_uid = decoded_token['uid']
        follower = User.objects.filter(uid_firebase=firebase_uid).first()
        followerUsername = request.data.get('target_username')
        following = User.objects.filter(username=followerUsername).first()
        if follower == following:
            return Response({'message:' 'Cannot follow yourself'})
        follow, created = Follow.objects.get_or_create(
            follower=follower,
            following=following
        )
        return Response({'message': 'Success', 'created': created})
