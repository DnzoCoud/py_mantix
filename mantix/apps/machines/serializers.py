from rest_framework import serializers
from .models import Machine, Status
from apps.locations.models import Location
from apps.locations.serializers import LocationSerializer

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'name']

class MachineSerializer(serializers.ModelSerializer):
    status = serializers.PrimaryKeyRelatedField(queryset=Status.objects.all(), write_only=True)
    status_detail = StatusSerializer(source='status', read_only=True)
    location = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all(), write_only=True)
    location_detail = LocationSerializer(source='location', read_only=True)
    class Meta:
        model = Machine
        fields = ['id','name', 'model', 'serial', 'last_maintenance', 'status','status_detail', 'location', 'location_detail']