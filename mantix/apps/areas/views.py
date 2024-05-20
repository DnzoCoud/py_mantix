from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from .models import Area
from .serializers import AreaSerializer


# Create your views here.
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def findAll():
    try:
        areas = Area.objects.filter(is_active=1)
        serializer = AreaSerializer(areas)
        return Response({'areas': serializer.data}, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def findById(id:int):
    try:
        area = Area.objects.filter(id=id,is_active=1).first()
        serializer = AreaSerializer(area)
        return Response({'area': serializer.data}, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def save(request):
    try:
        request.data['created_by'] = request.user
        serializer = AreaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"area": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)            
    except Exception as ex:
        return Response({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)