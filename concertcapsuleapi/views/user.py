from django.http import HttpResponseServerError
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from concertcapsuleapi.models import User


class UserView(ViewSet):
    def create(self, request):
        """Handle POST requests to create a new user"""
        user = User.objects.create(
            uid_firebase=request.data["uid_firebase"],
            username=request.data["username"],
            first_name=request.data.get("first_name", None),
            last_name=request.data.get("last_name", None)
        )
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """
        GET /users/:uid/
        Fetch user profile by Firebase UID
        """
        try:
            user = User.objects.get(uid_firebase=pk)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            # return null if user doesn't exist
            return Response(None, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def availability(self, request):
        search_param = request.GET.get('username', '')
        exists = User.objects.filter(username__iexact=search_param).exists()
        return Response({"available": not exists})


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'uid_firebase', 'username', 'first_name', 'last_name')
