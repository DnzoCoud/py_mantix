from rest_framework import serializers
from .models import Event, Status
from apps.machines.models import Machine
from apps.machines.serializers import MachineSerializer


class StatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = Status
        fields = ['id', 'name']

class EventSerializer(serializers.ModelSerializer):
    status = serializers.PrimaryKeyRelatedField(queryset=Status.objects.all(), write_only=True)
    status_detail = StatusSerializer(source='status', read_only=True)
    machine = serializers.PrimaryKeyRelatedField(queryset=Machine.objects.all(), write_only=True)
    machine_detail = MachineSerializer(source='machine', read_only=True)
    class Meta:
        model = Event
        fields = ['id', 'start', 'end', 'machine', 'machine_detail', 'status', 'status_detail']
