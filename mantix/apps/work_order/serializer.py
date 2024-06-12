from rest_framework import serializers
from .models import WorkOrder
from apps.events.models import Event
from apps.events.serializers import EventSerializer

class WorkOrderSerializer(serializers.ModelSerializer):
    event = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all(), write_only=True)
    event_detail = EventSerializer(source='event', read_only=True)
    class Meta:
        model = WorkOrder
        fields = [
            'id',
            'diagnosis',
            'observation',
            'cause',
            'event',
            'event_detail'
        ]