from rest_framework import serializers
from .models import Event, Status, Activity, Day, HistoryStatus, MaintenanceHistory
from apps.machines.models import Machine
from apps.machines.serializers import MachineSerializer
from apps.sign.models import User
from apps.sign.serializers import UserDetailSerializer
from datetime import datetime


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ["id", "name", "icon"]


class ActivitySerializer(serializers.ModelSerializer):
    technical = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True
    )
    technical_detail = UserDetailSerializer(source="technical", read_only=True)

    class Meta:
        model = Activity
        fields = ["id", "name", "completed", "technical", "technical_detail"]


class DaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Day
        fields = ["id", "date", "closed"]


class HistoryStatusSerializer(serializers.ModelSerializer):
    previous_state = StatusSerializer()
    actual_state = StatusSerializer()

    class Meta:
        model = HistoryStatus
        fields = ["id", "previous_state", "actual_state"]


class EventSerializer(serializers.ModelSerializer):
    end_time = serializers.TimeField(format="%H:%M:%S")
    status = serializers.PrimaryKeyRelatedField(
        queryset=Status.objects.all(), write_only=True
    )
    status_detail = StatusSerializer(source="status", read_only=True)
    machine = serializers.PrimaryKeyRelatedField(
        queryset=Machine.objects.all(), write_only=True
    )
    machine_detail = MachineSerializer(source="machine", read_only=True)
    activities = ActivitySerializer(many=True, read_only=True)  # Add this line
    day = serializers.PrimaryKeyRelatedField(
        queryset=Day.objects.all(), write_only=True
    )  # Campo para el día relacionado
    day_detail = DaySerializer(
        source="day", read_only=True
    )  # Campo detallado para el día relacionado

    history_status = HistoryStatusSerializer(required=False)
    request_user = UserDetailSerializer(required=False)

    class Meta:
        model = Event
        fields = [
            "id",
            "start",
            "end",
            "init_time",
            "end_time",
            "shift",
            "machine",
            "machine_detail",
            "status",
            "status_detail",
            "activities",
            "day",
            "day_detail",
            "history_status",
            "code",
            "request_user",
        ]

    def create(self, validated_data):
        activity_data = validated_data.pop("activity_data", [])
        event = Event.objects.create(**validated_data)
        for activity in activity_data:
            Activity.objects.create(event=event, **activity)
        return event

    # def get_history_statuses(self, obj):
    #     # Obtiene todos los HistoryStatus relacionados con el evento actual
    #     history_statuses = HistoryStatus.objects.filter(event=obj)
    #     return HistoryStatusSerializer(history_statuses, many=True).data


class MaintenanceHistorySerializer(serializers.ModelSerializer):
    machine = MachineSerializer()
    performed_by = UserDetailSerializer()
    status = StatusSerializer()

    class Meta:
        model = MaintenanceHistory
        fields = [
            "id",
            "maintenance_date",
            "description",
            "machine",
            "performed_by",
            "status",
        ]
