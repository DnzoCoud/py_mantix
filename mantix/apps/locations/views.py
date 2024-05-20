from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from .models import Location
from .serializers import LocationSerializer

# Create your views here.
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def findAll():
    try:
        locations = Location.objects.filter(is_active=1)
        serializer = LocationSerializer(locations)
        return Response({'locations': serializer.data}, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)