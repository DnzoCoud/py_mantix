import base64
import io
import pandas as pd
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import Machine
from .serializers import MachineSerializer
from rest_framework import status
from apps.locations.models import Location
from django.shortcuts import get_object_or_404

# Create your views here.

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def findAll(request):
    try:
        machines = Machine.objects.filter(status=1, deleted=False)
        serializer = MachineSerializer(machines, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def findById(request,id: int):
    try:
        machine = Machine.objects.filter( id=id,status=1, deleted=False).first()
        if not machine:
            return Response({'error': 'Esta maquina no existe o no se encuentra'}, status=status.HTTP_404_NOT_FOUND)
        serializer = MachineSerializer(machine)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def save(request):
    try:
        request.data['created_by'] = request.user
        serializer = MachineSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)            
    except Exception as ex:
        return Response({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update(request):
    try:
        id = request.data.get("id")
        if id is None:
            return Response({"error": "No se proporciona el id de la maquina que se va a actualizar"}, status=status.HTTP_400_BAD_REQUEST)

        name = request.data.get("name")
        model = request.data.get("model")
        serial = request.data.get("serial")
        last_maintenance = request.data.get("last_maintenance")
        location_id = request.data.get("location")
        machine = get_object_or_404(Machine, id=id)

        if name is not None:
            machine.name = name
        if model is not None:
            machine.model = model
        if serial is not None:
            machine.serial = serial
        if last_maintenance is not None:
            machine.last_maintenance = last_maintenance
        if location_id is not None:
            locationObject = get_object_or_404(Location, pk=location_id)
            machine.manager = locationObject
        machine.save()
        serializer = MachineSerializer(machine)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({"error": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete(request,id: int) :
    try:
        user = request.user
        machine = get_object_or_404(Machine, id=id)
        machine.delete(deleted_by=user)
        serializer = MachineSerializer(machine)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({"error": str(ex)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def importMachinesByExcel(request):
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
                    if 'Nombre de la maquina' in row.values and 'Modelo de la maquina' in row.values and 'Serial de la maquina' in row.values and 'Locación de la maquina' in row.values:
                        header_row_idx = i
                        break
                
                if header_row_idx is None:
                    return Response({"error": "No se encontró la fila del encabezado con las columnas esperadas"}, status=status.HTTP_400_BAD_REQUEST)
                
                # Establecer la fila del encabezado
                df.columns = df.iloc[header_row_idx]
                df = df.drop(index=list(range(0, header_row_idx + 1)))
                df.reset_index(drop=True, inplace=True)

                errors = []
                seen_machines = set()

                for index, row in df.iterrows():
                    machine_name = row['Nombre de la maquina']
                    location_name = row['Locación de la maquina']

                    if machine_name in seen_machines:
                        errors.append({'fila': index, 'columna': 'Nombre de la maquina', 'message': f'El nombre de la máquina "{machine_name}" está duplicado'})
                    else:
                        seen_machines.add(machine_name)
                    
                    if not Location.objects.filter(name=location_name).exists():
                        errors.append({'fila': index, 'columna': 'Locación de la maquina', 'message': f'La locación "{location_name}" no existe'})

                if errors:
                    return Response({'error': errors}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    machines = []
                    for index, row in df.iterrows():
                        machine_name = row['Nombre de la maquina']
                        machine_model = row['Modelo de la maquina']
                        machine_serial = row['Serial de la maquina']
                        location_name = row['Locación de la maquina']
                        location = Location.objects.filter(name=location_name.strip()).first()

                        machine = Machine.objects.create(
                            name=machine_name,
                            model=machine_model,
                            serial=machine_serial,
                            location=location
                        )
                        machines.append(machine)

                    serializer = MachineSerializer(machines, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as ex:
                return Response({"error": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"error": "No se proporcionó un excel en formato BASE64"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        return Response({"error": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)