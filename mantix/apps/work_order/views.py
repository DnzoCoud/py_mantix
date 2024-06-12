from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import WorkOrder
from .serializer import WorkOrderSerializer
from apps.events.models import Event
# Create your views here.
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def findAll(request) -> Response:
    try:
        workOrders = WorkOrder.objects.filter(deleted=False)
        serializer = WorkOrderSerializer(instance=workOrders, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({"error": str(ex)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def save(request: Request) -> Response:
    try:
        serializer = WorkOrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        return Response({"error": str(ex)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def findWorkOrderByEventId(request: Request, eventId:int):
    try:
        workOrder = get_object_or_404(WorkOrder, event=eventId)
        serializer = WorkOrderSerializer(workOrder)
        return Response(serializer.data,status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({"error": str(ex)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update(request: Request):
    try:
        id = request.data.get("id")
        if id is None:
            return Response({"error": "No se proporciona el id del workOrder que se va a actualizar"}, status=status.HTTP_400_BAD_REQUEST)

        diagnosis = request.data.get("diagnosis")
        observation = request.data.get("observation")
        event_id = request.data.get("event")
        cause = request.data.get("cause")

        workOrder = get_object_or_404(WorkOrder, id=id)

        if diagnosis is not None:
            workOrder.diagnosis = diagnosis
        if observation is not None:
            workOrder.observation = observation
        if cause is not None:
            workOrder.cause = cause
        if event_id is not None:
            eventObject = get_object_or_404(Event, pk=event_id)
            workOrder.event = eventObject
        workOrder.save()
        serializer = WorkOrderSerializer(workOrder)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as ex:
        return Response({"error": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
