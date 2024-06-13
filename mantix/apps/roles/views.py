from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from apps.roles.models import Role
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .serializers import RoleSerializer
# Create your views here.


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def findAllRoles(request:Request):
    try:
        # Verifica si hay roles en la base de datos que no sean ADMIN
        roles = Role.objects.all().exclude(pk=1)
        if not roles.exists():
            return Response({'error': 'No roles found'}, status=status.HTTP_404_NOT_FOUND)

        # Serializa los roles encontrados
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as ex:
        # Captura cualquier excepción y devuelve un error 500 con el mensaje de error
        return Response({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)