from rest_framework import serializers
from .models import Area
from apps.sign.models import User
from apps.sign.serializers import UserDetailSerializer

class AreaSerializer(serializers.ModelSerializer):
    director = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    director_detail = UserDetailSerializer(source='director', read_only=True) 
    class Meta:
        model = Area
        fields = ['id','name', 'director_detail', 'director']