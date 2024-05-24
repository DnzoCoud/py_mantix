from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

from .serializers import UserSerializer, UserDetailSerializer
from .models import User
from apps.roles.models import Role
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
# Create your views here.
@api_view(['POST'])
def login(request):
    user = get_object_or_404(User, email=request.data['email'])
    if not user.check_password(request.data['password']):
        return Response({"error": "Invalid Password"}, status=status.HTTP_400_BAD_REQUEST)
    
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(instance=user)
    return Response({"token": token.key, "user": serializer.data},status=status.HTTP_200_OK)

@api_view(['POST'])
def register(request: Request):
    role_id = request.data.get('role')
    password = request.data.get('password')
    if not password:
        return Response({"error": "El campo 'password' es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

    role = Role.objects.filter(id=role_id).first()
    if not role:
        return Response({"error": "El rol no existe"}, status=status.HTTP_404_NOT_FOUND)
    
    data = request.data.copy()
    data['role'] = role.id # Se asegura de que el rol es pasado correctamente como un ID
    data['password'] = password  # Encripta la contraseña antes de pasarla al serializador

    serializer = UserSerializer(data=data)
    
    if serializer.is_valid():
        serializer.save()
        user = User.objects.get(username=serializer.data['username'])
        user.set_password(serializer.data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_201_CREATED)
        
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    request.auth.delete()
    return Response("Se ha cerrado Sesion", status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def profile(request):
    return Response({"profile":request.user},status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def findUserDirectors(request):
    try:
        users = User.objects.filter(is_director=True)
        serializers = UserDetailSerializer(users, many=True)
        return Response(serializers.data,status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({"error":str(ex)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)