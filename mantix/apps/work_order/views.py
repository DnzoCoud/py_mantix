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
from apps.events.models import Event, Activity
from weasyprint import HTML
from django.template.loader import get_template
import base64
from django.conf import settings
from django.utils.dateformat import DateFormat

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


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def generateWorkOrderPDF(request:Request):
    logo_url = request.build_absolute_uri(settings.STATIC_URL + 'images/Logo.png')
    workOrder:WorkOrder = WorkOrder.objects.get(id=1)
    # Obtener la fecha del evento y formatearla
    event_date = workOrder.event.start
    day = DateFormat(event_date).format('d')
    month = DateFormat(event_date).format('M')
    year = DateFormat(event_date).format('Y')

    activities = Activity.objects.filter(event=workOrder.event.id)

    context = {
        "title":"Reporte PDF",
        "content":"Es te es el contenido generado desde django",
        "logo_url":logo_url,
        "machine_name": workOrder.event.machine.name,
        "diagnosis":workOrder.diagnosis,
        "day": day,
        "month": month,
        "year": year,
        "observation":workOrder.observation,
        "location_manager":f"{workOrder.event.machine.location.manager.first_name} {workOrder.event.machine.location.manager.last_name}",
        "activities":activities,
        "init_time":workOrder.event.init_time,
        "end_time":workOrder.event.end_time,

    
    }


    template = get_template('workOrder.html')
    html = template.render(context)

    pdf_file = HTML(string=html).write_pdf()

    pdf_base64 = base64.b64encode(pdf_file).decode('utf-8')
    return Response(pdf_base64, status=status.HTTP_201_CREATED)