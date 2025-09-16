from django.http import HttpResponseServerError
from rest_framework.response import Response
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from concertcapsuleapi.models import Concert, Artist, Venue, UserConcert, User, Follow
from firebase_admin import auth


class FollowView(viewsets.ModelViewSet):
    def create(self, request):
        """Handle POST requests to add a follow"""
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({'error': 'Missing auth'}, status=status.HTTP_401_UNAUTHORIZED)
        firebase_token = auth_header.split(' ')[1]
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

    @action(detail=False, methods=['delete'], url_path='unfollow')
    def unfollow(self, request):
        debug_info = {}

        username = request.query_params.get('username')
        debug_info['username'] = username

        auth_header = request.headers.get('Authorization')
        debug_info['has_auth_header'] = bool(auth_header)

        if not auth_header:
            return Response({
                'error': 'Missing auth',
                'debug': debug_info
            }, status=status.HTTP_401_UNAUTHORIZED)

        try:
            firebase_token = auth_header.split(' ')[1]
            decoded_token = auth.verify_id_token(firebase_token)
            debug_info['firebase_uid'] = decoded_token['uid']

            current_user = User.objects.filter(
                uid_firebase=decoded_token['uid']).first()
            debug_info['current_user_found'] = bool(current_user)
            debug_info['current_user_id'] = current_user.id if current_user else None

            target_user = User.objects.filter(username=username).first()
            debug_info['target_user_found'] = bool(target_user)
            debug_info['target_user_id'] = target_user.id if target_user else None

            follow_relationship = Follow.objects.filter(
                follower=current_user, following=target_user)
            debug_info['follow_relationship_exists'] = follow_relationship.exists()
            debug_info['follow_relationship_count'] = follow_relationship.count()

            if follow_relationship.exists():
                follow_relationship.delete()
                return Response({
                    'message': 'Unfollowed',
                    'debug': debug_info
                }, status=status.HTTP_204_NO_CONTENT)

            return Response({
                'message': 'Not following',
                'debug': debug_info
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            debug_info['error'] = str(e)
            return Response({
                'error': 'Internal server error',
                'debug': debug_info
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='follow_status')
    def follow_status(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            firebase_token = auth_header.split(' ')[1]
            decoded_token = auth.verify_id_token(firebase_token)
            firebase_uid = decoded_token['uid']
            current_user = User.objects.filter(
                uid_firebase=firebase_uid).first()
            target_username = request.query_params.get('username')
            target_user = User.objects.filter(username=target_username).first()
            follow_relationship = Follow.objects.filter(
                follower=current_user, following=target_user)
            following = follow_relationship.exists()
            return Response({'is_following': following})
