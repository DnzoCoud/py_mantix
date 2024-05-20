from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from .models import Location
from .serializers import LocationSerializer

import base64
import pandas as pd
from io import BytesIO


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
    
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def findById(id:int):
    try:
        location = Location.objects.filter( id=id,is_active=1).first()
        if not location:
            return Response({'error': 'Esta locacion no existe o esta inactiva'}, status=status.HTTP_404_NOT_FOUND)
        serializer = LocationSerializer(location)
        return Response({'location': serializer.data}, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def save(request):
    try:
        request.data['created_by'] = request.user
        serializer = LocationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"location": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)            
    except Exception as ex:
        return Response({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def import_locations(request:Request):
    file_data = request.data.get('file')
    if not file_data:
        return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        file_content = base64.b64decode(file_data)
    except base64.binascii.Error:
        return Response({"error": "Invalid base64 file"}, status=status.HTTP_400_BAD_REQUEST)

    # Detect file type by trying to read it with pandas
    try:
        data = pd.read_csv(BytesIO(file_content))
    except Exception as e_csv:
        try:
            data = pd.read_excel(BytesIO(file_content))
        except Exception as e_xlsx:
            return Response({"error": "Unsupported file format or corrupted file"}, status=status.HTTP_400_BAD_REQUEST)

    errors = []
    valid_data = []

    for index, row in data.iterrows():
        if not row['name'] or not row['manager']:
            errors.append(f"Row {index} is invalid")
            continue

        valid_data.append({
            'name': row['name'],
            'manager': row['age'],
        })

    if errors:
        return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
