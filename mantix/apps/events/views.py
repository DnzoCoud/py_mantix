from django.shortcuts import render
from django.db.models import Case, When, IntegerField
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import Event, Status, Activity, Day, HistoryStatus, MaintenanceHistory
from .serializers import *
from datetime import datetime, timedelta
import base64
import io
import pandas as pd
from apps.machines.models import Machine
from apps.sign.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from apps.constants import *
from django.db import transaction

# Create your views here.


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def findAll(request) -> Response:
    try:

        auth_user = request.user
        if auth_user.role.id == 7:
            events = (
                Event.objects.filter(
                    deleted=False, machine__location__area__director=auth_user.id
                )
                .annotate(
                    shift_order=Case(
                        When(shift="A", then=0),
                        When(shift="B", then=1),
                        When(shift="K", then=2),
                        output_field=IntegerField(),
                    )
                )
                .order_by("shift_order")
            )
        else:
            events = (
                Event.objects.filter(deleted=False)
                .annotate(
                    shift_order=Case(
                        When(shift="A", then=0),
                        When(shift="B", then=1),
                        When(shift="K", then=2),
                        output_field=IntegerField(),
                    )
                )
                .order_by("shift_order")
            )
        serializer = EventSerializer(instance=events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response(
            {"error": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def findById(request, id: int) -> Response:
    try:
        event = get_object_or_404(Event, id=id)
        serializer = EventSerializer(event)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response(
            {"error": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def save(request: Request) -> Response:
    try:
        start_date = request.data.get("start")

        # Verificar si el día existe en Day
        day_exists = Day.objects.filter(date=start_date).exists()

        if not day_exists:
            # Si no existe, crear el día
            day = Day.objects.create(date=start_date)
        else:
            # Si existe, verificar si está cerrado
            day = Day.objects.get(date=start_date)
            if day.closed:
                return Response(
                    {"error": "No se pueden crear eventos en fechas cerradas."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        request.data["created_by"] = request.user.id
        request.data["day"] = day.id
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            event = serializer.save()
            # WebSocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "events",  # Nombre del grupo al que enviar el mensaje
                {
                    "type": "event_created",  # Tipo de mensaje
                    "event_id": event.id,
                    "event_data": serializer.data,  # Datos del evento
                },
            )
            generate_history_for_maintenance(
                event.machine,
                event.status,
                "Se programa el mantenimiento",
                request.user,
                event.code,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as ex:
        return Response(
            {"error": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def convert_iso_date_to_yyyymmdd(iso_date_str):
    try:
        # Intenta convertir la cadena ISO 8601 a un objeto datetime
        iso_date = datetime.strptime(iso_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        # Formatea la fecha a YYYY-MM-DD si iso_date es válido
        formatted_date = iso_date.strftime("%Y-%m-%d")
        return formatted_date
    except ValueError:
        # Si no se puede convertir según el formato ISO 8601, devuelve la cadena original
        return iso_date_str


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def reprogram_request(request: Request):
    try:  # Se deduce que ya existe un registro en el historial de estado del evento
        event_id = request.data.get("event")
        action = request.data.get("action", "false")
        # action = str_to_bool(action)
        event = get_object_or_404(Event, id=event_id)
        history = HistoryStatus.objects.filter(event=event.id)
        history_instance = history.first()
        if action:  # Aceptaron la reprogramacion
            status_reprogram = get_object_or_404(
                Status, id=EventStatusEnum.REPROGRAMADO.value
            )
            history_instance.actual_state = status_reprogram
            event.status = status_reprogram

            generate_history_for_maintenance(
                event.machine,
                status_reprogram,
                "Se acepta la peticiòn para reprogramar el mantenimiento",
                request.user,
                event.code,
            )
        else:  # rechazaron la reprogramacio
            if history_instance.previous_reprogram:
                status_reprogram = get_object_or_404(
                    Status, id=EventStatusEnum.REPROGRAMADO.value
                )
                history_instance.actual_state = status_reprogram
                event.status = status_reprogram
            else:
                event.status = history_instance.previous_state

            event.start = history_instance.prev_start
            event.end = history_instance.prev_end
            history_instance.prev_start = None
            history_instance.prev_end = None
            generate_history_for_maintenance(
                event.machine,
                history_instance.previous_state,
                "Se rechaza la peticiòn para reprogramar el mantenimiento",
                request.user,
                event.code,
            )
        event.save()
        history_instance.save()
        serializer = EventSerializer(event)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "events",  # Nombre del grupo al que enviar el mensaje
            {
                "type": "event_updated",  # Tipo de mensaje
                "event_id": event.id,
                "event_data": serializer.data,  # Datos del evento
            },
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as ex:
        return Response(
            {"error": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def convertir_a_time(hora_str):
    parsed_time = datetime.strptime(hora_str, "%H:%M:%S").time()
    return parsed_time


@api_view(["PATCH"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update(request):
    try:
        id = request.data.get("id")
        if id is None:
            return Response(
                {"error": "No se proporciona el id del evento que se va a actualizar"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        start = request.data.get("start")
        end = request.data.get("end")
        status_id = request.data.get("status")
        init_time = request.data.get("init_time")
        end_time = request.data.get("end_time")

        activities = request.data.get("activity_data")

        with transaction.atomic():
            event = get_object_or_404(Event, id=id)
            prev_start = event.start
            prev_end = event.end
            machine = Machine.objects.get(pk=event.machine.id)

            if start is not None:
                event.start = convert_iso_date_to_yyyymmdd(start)
            if end is not None:
                event.end = convert_iso_date_to_yyyymmdd(end)
            if init_time is not None:
                event.init_time = init_time
            if end_time is not None:
                event.end_time = convertir_a_time(end_time)
            if status_id is not None:
                status_object = get_object_or_404(Status, pk=status_id)
                history = HistoryStatus.objects.filter(event=event.id)
                if status_object.id == EventStatusEnum.REPROGRAMADO.value:
                    if history.exists():
                        history_instance = history.first()
                        # Actualizar los campos del historial
                        if status_id != event.status.id:
                            history_instance.previous_state = event.status
                        history_instance.actual_state = status_object
                        history_instance.save()
                    else:
                        history_instance = HistoryStatus(
                            event=event,
                            previous_state=(
                                event.status if status_id != event.status.id else None
                            ),
                            actual_state=status_object,
                        )
                        history_instance.save()
                    generate_history_for_maintenance(
                        machine,
                        status_object,
                        "Se reprograma el mantenimiento",
                        user,
                        event.code,
                    )
                if status_object.id == EventStatusEnum.COMPLETADO.value:
                    machine.last_maintenance = datetime.now().strftime("%Y-%m-%d")
                    machine.save()
                    generate_history_for_maintenance(
                        machine,
                        status_object,
                        "Se completa el mantenimiento",
                        user,
                        event.code,
                    )
                if status_object.id == EventStatusEnum.EN_EJECUCION.value:
                    generate_history_for_maintenance(
                        machine,
                        status_object,
                        "Se pone en ejecución el mantenimiento",
                        user,
                        event.code,
                    )
                if status_object.id == EventStatusEnum.PETICION_REPROGRAMADO.value:
                    history = HistoryStatus.objects.filter(event=event.id)
                    if history.exists():
                        history_instance = history.first()
                        if status_id != event.status.id:
                            if event.status.id == EventStatusEnum.REPROGRAMADO.value:
                                history_instance.previous_reprogram = True
                            else:
                                history_instance.previous_state = event.status
                        history_instance.actual_state = status_object
                        history_instance.prev_start = prev_start
                        history_instance.prev_end = prev_end
                        history_instance.save()
                    else:
                        history_instance = HistoryStatus(
                            event=event,
                            previous_state=(
                                event.status if status_id != event.status.id else None
                            ),
                            actual_state=status_object,
                            prev_start=prev_start,
                            prev_end=prev_end,
                        )
                        history_instance.save()
                    event.request_user = user

                    generate_history_for_maintenance(
                        machine,
                        status_object,
                        "Se hace petición para reprogramar el mantenimiento",
                        user,
                        event.code,
                    )
                event.status = status_object
                event.save()

            if activities is not None:
                for activity_data in activities:
                    tecnical = activity_data.get("technician")
                    if tecnical["id"] is not None:
                        userObject = get_object_or_404(User, pk=tecnical["id"])
                    activity_objects = activity_data.get("activities")
                    for activity in activity_objects:
                        activity_id = activity.get("id")
                        name = activity.get("name")
                        completed = activity.get("completed")

                        if activity_id:
                            activityObj = get_object_or_404(
                                Activity, id=activity_id, event=event
                            )
                            if activityObj.name != name:
                                activityObj.name = name
                                activityObj.save()
                            if activityObj.completed != completed:
                                activityObj.completed = completed
                                activityObj.save()
                            if activityObj.technical != userObject:
                                activityObj.technical = userObject
                                activityObj.save()

                        else:
                            Activity.objects.create(
                                event=event, name=name, technical=userObject
                            )

            event.updated_by = user
            event.save()
            serializer = EventSerializer(event)

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "events",  # Nombre del grupo al que enviar el mensaje
                {
                    "type": "event_updated",  # Tipo de mensaje
                    "event_id": event.id,
                    "event_data": serializer.data,  # Datos del evento
                },
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as ex:
        return Response(
            {"error": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete(request: Request, id: int):
    try:
        user = request.user
        event = get_object_or_404(Event, id=id)
        event.delete(deleted_by=user)
        serializer = EventSerializer(event)
        return Response(
            {"message": "El mantenimiento ha sido eliminado correctamente"},
            status=status.HTTP_200_OK,
        )
    except Exception as ex:
        return Response(
            {"error": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def restore(id: int):
    try:
        event = get_object_or_404(Event, id=id)
        event.restore()
        return Response(
            {"message": "El mantenimiento ha sido reactivado correctamente"},
            status=status.HTTP_200_OK,
        )
    except Exception as ex:
        return Response(
            {"error": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_history_for_machine(request: Request):
    try:
        machine_id = request.query_params.get("machine")
        machine = Machine.objects.get(pk=machine_id)
        history = MaintenanceHistory.objects.filter(machine=machine.id).order_by(
            "-maintenance_date"
        )
        serializer = MaintenanceHistorySerializer(history, many=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    except Exception as ex:
        return Response(
            {"error": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def findEventsByDate(request: Request):
    try:
        fecha_inicio = request.data.get("start")
        fecha_fin = request.data.get("end")

        if not fecha_inicio.strip():
            return Response(
                {"error": "La fecha de inicio no puede estar vacia"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        fecha_inicio = datetime.strptime(fecha_inicio.strip(), "%Y-%m-%d")
        fecha_fin = datetime.strptime(fecha_fin.strip(), "%Y-%m-%d")

        if fecha_inicio and fecha_fin:
            # Ambas fechas están presentes, filtrar por rango de fechas
            events = Event.objects.filter(start=fecha_inicio, end=fecha_fin)
        elif fecha_inicio:
            # Solo fecha de inicio está presente, filtrar eventos que comienzan en o después de la fecha de inicio
            events = Event.objects.filter(start__gte=fecha_inicio)
        else:
            # Solo fecha de fin está presente, filtrar eventos que terminan en o antes de la fecha de fin
            events = Event.objects.filter(end__lte=fecha_fin)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response(
            {"error": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def findEventsByDay(request: Request):
    try:
        auth_user = request.user

        fecha_especifica_str = request.query_params.get("start")
        if not fecha_especifica_str.strip():
            return Response(
                {"error": "La fecha no puede estar vacia"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        fecha_especifica = datetime.strptime(fecha_especifica_str, "%Y-%m-%d").date()
        fecha_inicio = datetime.combine(fecha_especifica, datetime.min.time())
        fecha_fin = fecha_inicio + timedelta(days=1)

        if auth_user.role.id == 7:
            events = (
                Event.objects.filter(
                    start__gte=fecha_inicio,
                    start__lt=fecha_fin,
                    machine__location__area__director=auth_user.id,
                )
                .annotate(
                    shift_order=Case(
                        When(shift="A", then=0),
                        When(shift="B", then=1),
                        When(shift="K", then=2),
                        output_field=IntegerField(),
                    )
                )
                .order_by("shift_order")
            )
        else:
            events = (
                Event.objects.filter(start__gte=fecha_inicio, start__lt=fecha_fin)
                .annotate(
                    shift_order=Case(
                        When(shift="A", then=0),
                        When(shift="B", then=1),
                        When(shift="K", then=2),
                        output_field=IntegerField(),
                    )
                )
                .order_by("shift_order")
            )
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response(
            {"error": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def importEventsByExcel(request: Request):
    try:
        excel_base64 = request.data.get("excel_base64", None)
        if excel_base64:
            try:
                excel_bytes = base64.b64decode(excel_base64)
                excel_io = io.BytesIO(excel_bytes)
                df = pd.read_excel(excel_io, header=None)

                # Find header row
                header_row_idx = None
                for i, row in df.iterrows():
                    if (
                        "Fecha Inicio" in row.values
                        and "Fecha Fin" in row.values
                        and "Maquina Afectada" in row.values
                    ):
                        header_row_idx = i
                        break

                if header_row_idx is None:
                    return Response(
                        {
                            "error": "No se encontró la fila del encabezado con las columnas esperadas"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Set the header row
                df.columns = df.iloc[header_row_idx]
                df = df.drop(index=list(range(0, header_row_idx + 1)))
                df.reset_index(drop=True, inplace=True)

                errors = []
                for index, row in df.iterrows():
                    try:
                        # Convert to string if it's a datetime object
                        start_date_str = (
                            row["Fecha Inicio"].strftime("%Y-%m-%d")
                            if isinstance(row["Fecha Inicio"], datetime)
                            else str(row["Fecha Inicio"])
                        )
                        end_date_str = (
                            row["Fecha Fin"].strftime("%Y-%m-%d")
                            if isinstance(row["Fecha Fin"], datetime)
                            else str(row["Fecha Fin"])
                        )
                        datetime.strptime(start_date_str, "%Y-%m-%d")
                        datetime.strptime(end_date_str, "%Y-%m-%d")
                    except ValueError:
                        errors.append(
                            {
                                "fila": index,
                                "columna": "Fecha Inicio / Fecha Fin",
                                "message": "Formato de fecha inválido",
                            }
                        )

                    machine_name = row["Maquina Afectada"]
                    if not Machine.objects.filter(name=machine_name).exists():
                        errors.append(
                            {
                                "fila": index,
                                "columna": "Maquina",
                                "message": f'La máquina "{machine_name}" no existe',
                            }
                        )

                if errors:
                    return Response(
                        {"error": errors}, status=status.HTTP_400_BAD_REQUEST
                    )
                else:
                    events = []
                    for index, row in df.iterrows():
                        start_date_str = (
                            row["Fecha Inicio"].strftime("%Y-%m-%d")
                            if isinstance(row["Fecha Inicio"], datetime)
                            else str(row["Fecha Inicio"])
                        )
                        end_date_str = (
                            row["Fecha Fin"].strftime("%Y-%m-%d")
                            if isinstance(row["Fecha Fin"], datetime)
                            else str(row["Fecha Fin"])
                        )
                        start_date = datetime.strptime(
                            start_date_str, "%Y-%m-%d"
                        ).date()
                        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                        machine_name = row["Maquina Afectada"]
                        machine = Machine.objects.filter(name=machine_name).first()
                        shift = row["Turno"]
                        statusObject = Status.objects.filter(id=1).first()

                        # Verificar si la fecha inicial existe en Day
                        if not Day.objects.filter(date=start_date).exists():
                            # Si no existe, crear el día
                            day = Day.objects.create(date=start_date)
                        else:
                            # Si existe, verificar si está cerrado
                            day = Day.objects.get(date=start_date)
                            if day.closed:
                                return Response(
                                    {
                                        "error": f"No se pueden crear eventos en la fecha {start_date} porque está cerrada"
                                    },
                                    status=status.HTTP_400_BAD_REQUEST,
                                )

                        event = Event.objects.create(
                            start=start_date,
                            end=end_date,
                            created_by=request.user,
                            machine=machine,
                            shift=shift,
                            status=statusObject,
                            day=day,
                        )

                        generate_history_for_maintenance(
                            machine,
                            statusObject,
                            "Se programa el mantenimiento",
                            request.user,
                            event.code,
                        )
                        events.append(event)

                    serializer = EventSerializer(events, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as ex:
                return Response(
                    {"error": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            return Response(
                {"error": "No se proporcionó un excel en formato BASE64"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except Exception as ex:
        return Response(
            {"error": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def close_day(request, day_id):
    try:
        day = Day.objects.get(id=day_id)
        if day.cerrar_dia():
            return Response(
                {"message": "Day closed successfully."}, status=status.HTTP_200_OK
            )
        return Response(
            {
                "error": "El dia no puede cerrar, verifique que todos los mantenimientos esten completos."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Day.DoesNotExist:
        return Response({"error": "Day not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as ex:
        return Response(
            {"error": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_technician_performance(request: Request):
    now = datetime.now().strftime("%Y-%m-%d")
    try:
        auh_user = request.user
        actividades = Activity.objects.filter(technical=auh_user.id, event__start=now)
        total_actividades = actividades.count()

        actividades_completadas = actividades.filter(completed=True).count()
        porcentaje_completado = (
            ((actividades_completadas / total_actividades) * 100)
            if actividades_completadas > 0
            else 0
        )

        return Response(
            {
                "total_actividades": total_actividades,
                "actividades_completadas": actividades_completadas,
                "porcentaje_completado": porcentaje_completado,
            }
        )
    except Exception as ex:
        return Response(
            {"error": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_activities_by_technical_and_event(request: Request):
    techinal_id = request.query_params.get("technical")
    event_id = request.query_params.get("event")

    try:
        technical = User.objects.get(pk=techinal_id)
    except User.DoesNotExist:
        return Response(
            {"error": "El tecnico no existe."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        event = Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        return Response(
            {"error": "El mantenimiento no existe."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    activities = Activity.objects.filter(technical=technical.id, event=event.id)
    serializer = ActivitySerializer(activities, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_events_by_technical(request: Request):
    techinal_id = request.query_params.get("technical")

    try:
        technical = User.objects.get(pk=techinal_id)
    except User.DoesNotExist:
        return Response(
            {"error": "El tecnico no existe."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    events = Event.objects.filter(activities__technical=technical.id).distinct()
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)


def generate_history_for_maintenance(
    machine: Machine, status: Status, description, performed_by: User, event_code
):
    now = datetime.now()
    history = MaintenanceHistory(
        machine=machine,
        status=status,
        maintenance_date=now,
        performed_by=performed_by,
        description=description,
        event_code=event_code,
    )

    history.save()
