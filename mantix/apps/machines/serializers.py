from rest_framework import serializers
from .models import Machine, Status

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'name']

class MachineSerializer(serializers.ModelSerializer):
    status = serializers.PrimaryKeyRelatedField(queryset=Status.objects.all(), write_only=True)
    status_detail = StatusSerializer(source='status', read_only=True)
    class Meta:
        model = Machine
        fields = ['name', 'model', 'serial', 'last_maintenance', 'status','status_detail']