from rest_framework import serializers
from concertcapsuleapi.models import Concert, UserConcert, User


class ConcertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concert
        fields = ('id', 'artist', 'venue', 'tour_name', 'date', 'time')
        depth = 1


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'uid_firebase', 'username', 'first_name', 'last_name')


class UsernameSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username',)


class ArtistSearchSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()


class UserConcertSerializer(serializers.ModelSerializer):
    concert = ConcertSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserConcert
        fields = ['id', 'concert', 'username', 'created_at']
