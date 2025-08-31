from rest_framework import viewsets, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import response
from concertcapsuleapi.models import Artist
from concertcapsuleapi.services import spotify_get
from concertcapsuleapi.serializers import ArtistSearchSerializer


class ArtistView(viewsets.ViewSet):
    @action(detail=False, methods=['get'])
    def search(self, request):
        search_param = request.GET.get('q', '')
        default_params = {
            'type': 'artist',
            'limit': 5
        }
        artist_search_params = {**default_params, 'q': search_param}
        results = spotify_get('search', artist_search_params)
        artists_data = results["artists"]["items"]
        serializer = ArtistSearchSerializer(artists_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
