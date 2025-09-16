import logging
from django.utils import timezone
from django.http import HttpResponseServerError
from rest_framework.response import Response
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from concertcapsuleapi.models import Concert, Artist, Venue, UserConcert, User, Follow
from firebase_admin import auth


class FollowView(viewsets.ModelViewSet):
    from rest_framework import viewsets, status


logger = logging.getLogger(__name__)


class FollowView(viewsets.ModelViewSet):
    """
    ViewSet for handling follow/unfollow operations with comprehensive debugging
    """

    def create(self, request):
        """Handle POST requests to add a follow"""

        # Initialize debug info that will be returned in response
        debug_info = {
            'timestamp': str(timezone.now()),
            'method': request.method,
            'path': request.path,
            'content_type': request.content_type,
            'step': 'initialized'
        }

        try:
            # Debug headers (mask sensitive info)
            debug_info['headers'] = {}
            for header_name, header_value in request.headers.items():
                if 'authorization' in header_name.lower():
                    if header_value and len(header_value) > 20:
                        masked_value = f"{header_value[:15]}...{header_value[-10:]}"
                    else:
                        masked_value = "***PRESENT***" if header_value else None
                    debug_info['headers'][header_name] = masked_value
                else:
                    debug_info['headers'][header_name] = header_value

            # Debug request data
            debug_info['request_data'] = dict(
                request.data) if hasattr(request, 'data') else {}
            debug_info['request_post'] = dict(
                request.POST) if hasattr(request, 'POST') else {}
            debug_info['step'] = 'request_data_captured'

            # Check for auth header
            auth_header = request.headers.get('Authorization')
            debug_info['auth_header_present'] = bool(auth_header)
            debug_info['auth_header_format'] = auth_header[:30] + \
                '...' if auth_header and len(
                    auth_header) > 30 else str(auth_header)

            if not auth_header:
                debug_info['step'] = 'no_auth_header'
                debug_info['available_headers'] = list(request.headers.keys())
                return Response({
                    'error': 'Missing auth',
                    'debug': debug_info
                }, status=status.HTTP_401_UNAUTHORIZED)

            debug_info['step'] = 'auth_header_found'

            # Validate auth header format
            if not auth_header.startswith('Bearer '):
                debug_info['step'] = 'invalid_auth_format'
                debug_info['auth_header_start'] = auth_header[:20]
                return Response({
                    'error': 'Invalid auth header format',
                    'debug': debug_info
                }, status=status.HTTP_401_UNAUTHORIZED)

            # Extract Firebase token
            firebase_token = auth_header.split(' ')[1]
            debug_info['token_extracted'] = True
            debug_info['token_preview'] = f"{firebase_token[:20]}...{firebase_token[-10:]}"
            debug_info['step'] = 'token_extracted'

            # Verify Firebase token
            decoded_token = auth.verify_id_token(firebase_token)
            firebase_uid = decoded_token['uid']
            debug_info['token_verified'] = True
            debug_info['firebase_uid'] = firebase_uid
            debug_info['token_audience'] = decoded_token.get('aud', 'N/A')
            debug_info['token_issuer'] = decoded_token.get('iss', 'N/A')
            debug_info['step'] = 'token_verified'

            # Get current user
            from .models import User  # Import your User model
            follower = User.objects.filter(uid_firebase=firebase_uid).first()
            debug_info['current_user_found'] = bool(follower)
            if follower:
                debug_info['current_user_id'] = follower.id
                debug_info['current_user_username'] = follower.username
            debug_info['step'] = 'current_user_lookup_complete'

            # Get target username
            target_username = request.data.get('target_username')
            debug_info['target_username'] = target_username
            debug_info['target_username_provided'] = bool(target_username)

            if not target_username:
                debug_info['step'] = 'no_target_username'
                return Response({
                    'error': 'target_username required',
                    'debug': debug_info
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get target user
            following = User.objects.filter(username=target_username).first()
            debug_info['target_user_found'] = bool(following)
            if following:
                debug_info['target_user_id'] = following.id
                debug_info['target_user_username'] = following.username
            debug_info['step'] = 'target_user_lookup_complete'

            # Validation checks
            if not follower:
                debug_info['step'] = 'current_user_not_found'
                return Response({
                    'error': 'Current user not found',
                    'debug': debug_info
                }, status=status.HTTP_400_BAD_REQUEST)

            if not following:
                debug_info['step'] = 'target_user_not_found'
                return Response({
                    'error': 'Target user not found',
                    'debug': debug_info
                }, status=status.HTTP_400_BAD_REQUEST)

            if follower == following:
                debug_info['step'] = 'self_follow_attempt'
                return Response({
                    'error': 'Cannot follow yourself',
                    'debug': debug_info
                }, status=status.HTTP_400_BAD_REQUEST)

            # Check existing relationship
            from .models import Follow  # Import your Follow model
            existing_follow = Follow.objects.filter(
                follower=follower, following=following).first()
            debug_info['already_following'] = bool(existing_follow)
            debug_info['step'] = 'relationship_check_complete'

            # Create or get follow relationship
            follow, created = Follow.objects.get_or_create(
                follower=follower,
                following=following
            )

            debug_info['follow_created'] = created
            debug_info['follow_id'] = follow.id
            debug_info['step'] = 'follow_relationship_processed'

            return Response({
                'message': 'Follow successful',
                'created': created,
                'debug': debug_info
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

        except Exception as e:
            debug_info['step'] = 'exception_occurred'
            debug_info['error_type'] = type(e).__name__
            debug_info['error_message'] = str(e)

            return Response({
                'error': f'Internal server error: {str(e)}',
                'debug': debug_info
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
