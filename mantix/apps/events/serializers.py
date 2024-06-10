from rest_framework import serializers
from .models import Event, Status, Activity
from apps.machines.models import Machine
from apps.machines.serializers import MachineSerializer


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'name']

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = [
            'id',
            'name',
            'completed'
        ]

class EventSerializer(serializers.ModelSerializer):
    status = serializers.PrimaryKeyRelatedField(queryset=Status.objects.all(), write_only=True)
    status_detail = StatusSerializer(source='status', read_only=True)
    machine = serializers.PrimaryKeyRelatedField(queryset=Machine.objects.all(), write_only=True)
    machine_detail = MachineSerializer(source='machine', read_only=True)
    activities = ActivitySerializer(many=True, read_only=True)  # Add this line
    class Meta:
        model = Event
        fields = ['id', 'start', 'end', 'init_time', 'end_time', 'machine', 'machine_detail', 'status', 'status_detail','activities']

    def create(self, validated_data):
        activity_data = validated_data.pop('activity_data', [])
        event = Event.objects.create(**validated_data)
        for activity in activity_data:
            Activity.objects.create(event=event, **activity)
        return event