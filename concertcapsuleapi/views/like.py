from django.http import HttpResponseServerError
from rest_framework.response import Response
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from concertcapsuleapi.models import UserConcert, User, Like
from firebase_admin import auth
from concertcapsuleapi.serializers import LikeSerializer


class LikeView(viewsets.ModelViewSet):
    def create(self, request):
        """Handle POST requests to add a like"""
        firebase_token = request.data.get('firebase_token')
        decoded_token = auth.verify_id_token(firebase_token)
        firebase_uid = decoded_token['uid']
        user = User.objects.filter(uid_firebase=firebase_uid).first()
        user_concert = request.data.get('user_concert')
        user_concert_instance = UserConcert.objects.get(pk=user_concert)
        like = Like.objects.create(
            user=user,
            user_concert=user_concert_instance
        )

        serializer = LikeSerializer(like)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['delete'])
    def unlike_concert(self, request):
        """Handle DELETE requests to un-like a concert"""
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            firebase_token = auth_header.split(' ')[1]
            decoded_token = auth.verify_id_token(
                firebase_token, clock_skew_seconds=30)
            firebase_uid = decoded_token['uid']
            current_user = User.objects.filter(
                uid_firebase=firebase_uid).first()
            user_concert = request.data.get('user_concert')

            try:
                user_concert_instance = UserConcert.objects.get(
                    pk=user_concert)
                like = Like.objects.get(  # Fixed: get the object first
                    user=current_user,
                    user_concert=user_concert_instance
                )
                like.delete()  # Then delete it
                return Response({'message': 'Like removed'}, status=status.HTTP_200_OK)
            except (UserConcert.DoesNotExist, Like.DoesNotExist):
                return Response({'error': 'Like not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
