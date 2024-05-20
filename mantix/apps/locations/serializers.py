from rest_framework import serializers
from .models import Location
from apps.sign.models import User
from apps.sign.serializers import UserSerializer
from apps.areas.models import Area
from apps.areas.serializers import AreaSerializer

class LocationSerializer(serializers.ModelSerializer):
    manager = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    manager_detail = UserSerializer(source='manager', read_only=True) 
    area = serializers.PrimaryKeyRelatedField(queryset=Area.objects.all(), write_only=True)
    area_detail = AreaSerializer(source='area', read_only=True) 
    class Meta:
        model =Location
        fields = ['id','name', 'area_detail', 'area', 'manager_detail', 'manager']