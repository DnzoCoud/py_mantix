from rest_framework import serializers
from .models import Role, Menu, Role_Menu


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ["id", "name", "icon", "tooltip", "link"]


class RoleMenuSerializer(serializers.ModelSerializer):
    menu_detail = MenuSerializer(source="menu", read_only=True)

    class Meta:
        model = Role_Menu
        fields = ["id", "menu_detail"]


class RoleSerializer(serializers.ModelSerializer):
    menus = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ["id", "name", "menus", "icon"]

    def get_menus(self, obj):
        role_menus = Role_Menu.objects.filter(role=obj)
        return RoleMenuSerializer(role_menus, many=True).data
