import base64
import io
import pandas as pd
import re
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from .models import Area
from .serializers import AreaSerializer
from apps.sign.models import User
from django.shortcuts import get_object_or_404

# Create your views here.
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def findAll(request):
    try:
        areas = Area.objects.filter(is_active=1)
        serializer = AreaSerializer(areas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def findById(request,id:int):
    try:
        area = Area.objects.filter(id=id,is_active=1).first()
        serializer = AreaSerializer(area)
        return Response(serializer.data, status=status.HTTP_200_OK)
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
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)            
    except Exception as ex:
        return Response({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update(request: Request):
    try:
        id = request.data.get("id")
        if id is None:
            return Response({"error": "No se proporciona el id del area que se va a actualizar"}, status=status.HTTP_400_BAD_REQUEST)

        name = request.data.get("name")
        director_id = request.data.get("director_id")

        area = get_object_or_404(Area, id=id)

        if name is not None:
            area.name = name
        if director_id is not None:
            userObject = get_object_or_404(User, pk=director_id)
            area.director = userObject
        area.save()
        serializer = AreaSerializer(area)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as ex:
        return Response({"error": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete(request: Request,id: int) :
    try:
        user = request.user
        area = get_object_or_404(Area, id=id)
        area.delete(deleted_by=user)
        serializer = AreaSerializer(area)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({"error": str(ex)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def importAreasByExcel(request: Request):
    try:
        excel_base64 = request.data.get('excel_base64', None)
        if excel_base64:
            try:
                excel_bytes = base64.b64decode(excel_base64)
                excel_io = io.BytesIO(excel_bytes)
                df = pd.read_excel(excel_io, header=None)
                
                # Find header row
                header_row_idx = None
                for i, row in df.iterrows():
                    if 'Nombre de área' in row.values and 'Nombre director de área' in row.values:
                        header_row_idx = i
                        break
                
                if header_row_idx is None:
                    return Response({"error": "No se encontró la fila del encabezado con las columnas esperadas"}, status=status.HTTP_400_BAD_REQUEST)
                
                # Set the header row
                df.columns = df.iloc[header_row_idx]
                df = df.drop(index=list(range(0, header_row_idx + 1)))
                df.reset_index(drop=True, inplace=True)

                errors = []
                seen_areas = set()
                
                # Regular expression for validating an Email
                email_regex = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

                for index, row in df.iterrows():
                    area_name = row['Nombre de área']
                    director_info = row['Nombre director de área']

                    if area_name in seen_areas:
                        errors.append({'fila': index, 'columna': 'Nombre de área', 'message': f'El nombre de área "{area_name}" está duplicado'})
                    else:
                        seen_areas.add(area_name)
                    
                    if email_regex.match(director_info):
                        director = User.objects.filter(email=director_info).first()
                    else:
                        director = User.objects.filter(username=director_info).first()

                    if not director:
                        errors.append({'fila': index, 'columna': 'Nombre director de área', 'message': f'El director "{director_info}" no existe'})

                if errors:
                    return Response({'error': errors}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    areas = []
                    for index, row in df.iterrows():
                        area_name = row['Nombre de área']
                        director_info = row['Nombre director de área']
                        if email_regex.match(director_info):
                            director = User.objects.filter(email=director_info).first()
                        else:
                            director = User.objects.filter(username=director_info).first()

                        area = Area.objects.create(
                            name=area_name,
                            director=director
                        )
                        areas.append(area)

                    serializer = AreaSerializer(areas, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as ex:
                return Response({"error": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"error": "No se proporcionó un excel en formato BASE64"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        return Response({"error": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)