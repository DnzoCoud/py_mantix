from rest_framework import serializers
from .models import User
from apps.roles.models import Role
from apps.roles.serializers import RoleSerializer


class UserSerializer(serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), write_only=True)
    role_detail = RoleSerializer(source='role', read_only=True)  # Campo de solo lectura para la representación del rol
    class Meta:
        model = User
        fields = [
            'id', 
            'username', 
            'email', 
            'password', 
            'first_name', 
            'last_name', 
            'is_director', 
            'is_manager',
            'role',
            'role_detail'
        ]

class UserDetailSerializer(serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), write_only=True)
    role_detail = RoleSerializer(source='role', read_only=True)  # Campo de solo lectura para la representación del rol
    class Meta:
        model = User
        fields = [
            'id', 
            'username', 
            'email',
            'first_name', 
            'last_name', 
            'is_director', 
            'is_manager',
            'role',
            'role_detail'
        ]