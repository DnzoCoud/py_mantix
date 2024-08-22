from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from apps.roles.models import Role, Menu, Role_Menu
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .serializers import RoleSerializer, MenuSerializer
from django.db import transaction

# Create your views here.


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def findAllRoles(request: Request):
    try:
        # Verifica si hay roles en la base de datos que no sean ADMIN
        roles = Role.objects.all().exclude(pk=1)
        if not roles.exists():
            return Response(
                {"error": "No roles found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Serializa los roles encontrados
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as ex:
        # Captura cualquier excepción y devuelve un error 500 con el mensaje de error
        return Response(
            {"error": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def findAllMenus(request: Request):
    try:
        # Verifica si hay roles en la base de datos que no sean ADMIN
        menus = Menu.objects.all()
        if not menus.exists():
            return Response(
                {"error": "No roles found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Serializa los roles encontrados
        serializer = MenuSerializer(menus, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as ex:
        # Captura cualquier excepción y devuelve un error 500 con el mensaje de error
        return Response(
            {"error": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["PUT"])
def update_role_menus(request):
    roles_change = request.data.get("roleChange", [])

    for role_change in roles_change:
        role_id = role_change.get("roleId")
        menus = role_change.get("menus", [])

        # Validar que haya al menos un menú
        if not menus:
            return Response(
                {"error": "Debe haber al menos un menú asociado al rol."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            role = Role.objects.get(pk=role_id)
        except Role.DoesNotExist:
            return Response(
                {"error": "Role not found"}, status=status.HTTP_404_NOT_FOUND
            )

        menu_ids = [menu.get("id") for menu in menus]

        # Usar una transacción para asegurar la integridad de los datos
        with transaction.atomic():
            # Actualizar los menús asociados al rol
            role.menus.set(menu_ids)

        # Serializar la respuesta
        serializer = RoleSerializer(role)
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(
        {"error": "Invalid data format."},
        status=status.HTTP_400_BAD_REQUEST,
    )
