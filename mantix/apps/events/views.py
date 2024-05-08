from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import Event, Status
from .serializers import *

# Create your views here.

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def findAll() -> Response:
    try:
        events = Event.objects.all()
        serializer = EventSerializer(instance=events)
        return Response({"events": serializer.data},status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({"error": str(ex)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def findById(id: int) -> Response:
    try:
        event = get_object_or_404(Event, id=id)
        serializer = EventSerializer(event)
        return Response({"event": serializer.data},status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({"error": str(ex)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def save(request: Request) -> Response:
    try:
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"event": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        return Response({"error": str(ex)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)