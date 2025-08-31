from rest_framework.decorators import api_view
from rest_framework.response import Response
from concertcapsuleapi.models import Follow, UserConcert, User
from firebase_admin import auth
from concertcapsuleapi.serializers import UserConcertSerializer


@api_view(['GET'])
def news_feed(request):
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        firebase_token = auth_header.split(' ')[1]
        decoded_token = auth.verify_id_token(firebase_token)
        firebase_uid = decoded_token['uid']
        current_user = User.objects.filter(
            uid_firebase=firebase_uid).first()
        following_users = Follow.objects.filter(
            follower=current_user
        ).values_list('following', flat=True)
        news_feed_items = UserConcert.objects.filter(
            user__in=following_users
        ).select_related('user', 'concert').order_by('-created_at')[:50]

        serializer = UserConcertSerializer(news_feed_items, many=True)
        return Response(serializer.data)
