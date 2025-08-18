from rest_framework import viewsets, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import response
from concertcapsuleapi.models import Venue
from concertcapsuleapi.services import setlist_fm_get


class VenueSearchSerializer(serializers.Serializer):
    setlist_fm_id = serializers.CharField(source='id')
    name = serializers.CharField()
    city = serializers.CharField(
        source='city.name', required=False, allow_blank=True)
    state = serializers.CharField(
        source='city.state', required=False, allow_blank=True)


class VenueView(viewsets.ViewSet):
    @action(detail=False, methods=['get'])
    def search(self, request):
        search_param = request.GET.get('q', '')
        venue_search_params = {
            'p': 1,
            'name': search_param,
            'country': 'US'
        }
        results = setlist_fm_get('search/venues', venue_search_params)
        venue_data = results["venue"]
        serializer = VenueSearchSerializer(venue_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
