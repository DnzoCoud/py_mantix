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
from .models import Location
from .serializers import LocationSerializer
from apps.areas.models import Area
from apps.sign.models import User
from django.shortcuts import get_object_or_404



# Create your views here.
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def findAll(request):
    try:
        locations = Location.objects.filter(deleted=False)
        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def findById(request,id:int):
    try:
        location = Location.objects.filter( id=id,deleted=False).first()
        if not location:
            return Response({'error': 'Esta locacion no existe o esta inactiva'}, status=status.HTTP_404_NOT_FOUND)
        serializer = LocationSerializer(location)
        return Response(serializer.data, status=status.HTTP_200_OK)
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
            return Response({"error": "No se proporciona el id de la locacion que se va a actualizar"}, status=status.HTTP_400_BAD_REQUEST)

        name = request.data.get("name")
        manager_id = request.data.get("manager_id")
        area_id = request.data.get("area_id")


        locacion = get_object_or_404(Location, id=id)

        if name is not None:
            locacion.name = name
        if manager_id is not None:
            userObject = get_object_or_404(User, pk=manager_id)
            locacion.manager = userObject
        if area_id is not None:
            areaObject = get_object_or_404(Area, pk=area_id)
            locacion.manager = areaObject
        locacion.save()
        serializer = LocationSerializer(locacion)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({"error": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete(request: Request,id: int) :
    try:
        user = request.user
        location = get_object_or_404(Location, id=id)
        location.delete(deleted_by=user)
        serializer = LocationSerializer(location)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({"error": str(ex)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def importLocationsByExcel(request):
    try:
        excel_base64 = request.data.get('excel_base64', None)
        if excel_base64:
            try:
                excel_bytes = base64.b64decode(excel_base64)
                excel_io = io.BytesIO(excel_bytes)
                df = pd.read_excel(excel_io, header=None)
                
                # Encontrar la fila del encabezado
                header_row_idx = None
                for i, row in df.iterrows():
                    if 'Nombre de locación' in row.values and 'Nombre mánager de locación' in row.values and 'Area a la que pertenece' in row.values:
                        header_row_idx = i
                        break
                
                if header_row_idx is None:
                    return Response({"error": "No se encontró la fila del encabezado con las columnas esperadas"}, status=status.HTTP_400_BAD_REQUEST)
                
                # Establecer la fila del encabezado
                df.columns = df.iloc[header_row_idx]
                df = df.drop(index=list(range(0, header_row_idx + 1)))
                df.reset_index(drop=True, inplace=True)

                errors = []

                for index, row in df.iterrows():
                    location_name = row['Nombre de locación'].strip()
                    manager_name_or_email = row['Nombre mánager de locación'].strip()
                    area_name = row['Area a la que pertenece'].strip()

                    # Validar manager de locación (por correo o nombre de usuario)
                    if re.match(r"[^@]+@[^@]+\.[^@]+", manager_name_or_email):  # Validar si es un correo electrónico
                        manager = User.objects.filter(email=manager_name_or_email).first()
                        if not manager:
                            errors.append({'fila': index, 'columna': 'Nombre mánager de locación', 'message': f'El manager con correo "{manager_name_or_email}" no existe'})
                    else:
                        manager = User.objects.filter(username=manager_name_or_email).first()
                        if not manager:
                            errors.append({'fila': index, 'columna': 'Nombre mánager de locación', 'message': f'El manager con username "{manager_name_or_email}" no existe'})

                    # Validar área de la locación
                    area = Area.objects.filter(name=area_name).first()
                    if not area:
                        errors.append({'fila': index, 'columna': 'Area a la que pertenece', 'message': f'El área "{area_name}" no existe'})

                if errors:
                    return Response({'error': errors}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    locations = []
                    for index, row in df.iterrows():
                        location_name = row['Nombre de locación'].strip()
                        manager_name_or_email = row['Nombre mánager de locación'].strip()
                        area_name = row['Area a la que pertenece'].strip()

                        # Obtener el manager de locación
                        if re.match(r"[^@]+@[^@]+\.[^@]+", manager_name_or_email):
                            manager = User.objects.filter(email=manager_name_or_email).first()
                        else:
                            manager = User.objects.filter(username=manager_name_or_email).first()

                        # Obtener el área de la locación
                        area = Area.objects.filter(name=area_name).first()

                        location, created = Location.objects.update_or_create(
                            name=location_name,
                            defaults={
                                'manager': manager,
                                'area': area
                            }
                        )
                        locations.append(location)

                    serializer = LocationSerializer(locations, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as ex:
                return Response({"error": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"error": "No se proporcionó un excel en formato BASE64"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        return Response({"error": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
