from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import Machine
from .serializers import MachineSerializer
from rest_framework import status
# Create your views here.

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def findAll(request):
    try:
        machines = Machine.objects.filter(status=1)
        serializer = MachineSerializer(machines, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def findById(request,id: int):
    try:
        machine = Machine.objects.filter( id=id,status=1).first()
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