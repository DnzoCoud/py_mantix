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
from datetime import datetime
# Create your views here.

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def findAll() -> Response:
    try:
        events = Event.objects.filter(delete=False)
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
        return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        return Response({"error": str(ex)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update(request: Request, id:int):
    try:
        start = request.POST.get("start")
        end = request.POST.get("end")
        status_id = request.POST.get("status")

        event = get_object_or_404(Event, id=id)

        if start is not None:
            event.start = start
        if end is not None:
            event.end = end
        if status_id is not None:
            status = get_object_or_404(Status, pk=status_id)
            event.status = status

        updatedEvent = event.save()
        serializer = EventSerializer(updatedEvent)
        return Response({"event": serializer.data}, status=status.HTTP_201_CREATED)
    except Exception as ex:
        return Response({"error": str(ex)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete(id: int) :
    try:
        event = get_object_or_404(Event, id=id)
        event.delete()
        return Response({"message": 'El mantenimiento ha sido eliminado correctamente'}, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({"error": str(ex)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def restore(id: int) :
    try:
        event = get_object_or_404(Event, id=id)
        event.restore()
        return Response({"message": 'El mantenimiento ha sido reactivado correctamente'}, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({"error": str(ex)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def findEventsByDate(request: Request):
    try:
        fecha_inicio = request.POST.get('start')
        fecha_fin = request.POST.get('end')

        if not fecha_inicio.strip():
            return Response({"error": "La fecha de inicio no puede estar vacia"}, status=status.HTTP_400_BAD_REQUEST)

        fecha_inicio = datetime.strptime(fecha_inicio.strip(), '%Y-%m-%d')
        fecha_fin = datetime.strptime(fecha_fin.strip(), '%Y-%m-%d')

        if fecha_inicio and fecha_fin:
            # Ambas fechas están presentes, filtrar por rango de fechas
            events = Event.objects.filter(start=fecha_inicio, end=fecha_fin)
        elif fecha_inicio:
            # Solo fecha de inicio está presente, filtrar eventos que comienzan en o después de la fecha de inicio
            events = Event.objects.filter(start__gte=fecha_inicio)
        else:
            # Solo fecha de fin está presente, filtrar eventos que terminan en o antes de la fecha de fin
            events = Event.objects.filter(end__lte=fecha_fin)
        serializer = EventSerializer(events)
        return Response({"events": serializer.data}, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({"error": str(ex)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def findEventsByDay(request: Request):
    try:
        fecha_especifica_str = request.POST.get('start')
        if not fecha_especifica_str.strip():
            return Response({"error": "La fecha no puede estar vacia"}, status=status.HTTP_400_BAD_REQUEST)
        
        fecha_especifica = datetime.strptime(fecha_especifica_str, '%Y-%m-%d')
        events = Event.objects.filter(start__date=fecha_especifica)
        serializer = EventSerializer(events)
        return Response({"events": serializer.data}, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({"error": str(ex)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
