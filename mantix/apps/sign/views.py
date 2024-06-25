import base64
import io
import pandas as pd
import re
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
from enum import Enum
from apps.roles.serializers import RoleSerializer


class Roles(Enum):
    ADMIN = 1
    GUEST = 2
    VISUALIZER = 3
    TECHNICAL = 4
    PROVIDER = 5 
    MANAGER = 6
    DIRECTOR = 7

# Create your views here.


@api_view(['POST'])
def login(request):
    user = get_object_or_404(User, email=request.data['email'])
    if not user.is_active:
        return Response({"error": "Usuario deshabilitado"}, status=status.HTTP_400_BAD_REQUEST)

    if not user.check_password(request.data['password']):
        return Response({"error": "Invalid Password"}, status=status.HTTP_400_BAD_REQUEST)
    
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(instance=user)
    return Response({"token": token.key, "user": serializer.data},status=status.HTTP_200_OK)

@api_view(['POST'])
def loginTechnical(request):
    user = get_object_or_404(User, email=request.data['email'], role=Roles.TECHNICAL.value)
    if not user.is_active:
        return Response({"error": "Usuario deshabilitado"}, status=status.HTTP_400_BAD_REQUEST)
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
    return Response(request.user,status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def findUserDirectors(request):
    try:
        users = User.objects.filter(is_director=True, role=Roles.DIRECTOR.value, is_active=True)
        serializers = UserDetailSerializer(users, many=True)
        return Response(serializers.data,status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({"error":str(ex)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def findAll(request):
    try:
        users = User.objects.filter(is_active=True).exclude(role=Roles.ADMIN.value)
        serializers = UserDetailSerializer(users, many=True)
        return Response(serializers.data,status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({"error":str(ex)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def findManagers(request):
    try:
        users = User.objects.filter(is_manager=True, role=Roles.MANAGER.value)
        serializers = UserDetailSerializer(users, many=True)
        return Response(serializers.data,status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({"error":str(ex)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def findTechnicals(request):
    try:
        users = User.objects.filter(role=Roles.TECHNICAL.value)
        serializers = UserDetailSerializer(users, many=True)
        return Response(serializers.data,status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({"error":str(ex)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def findById(request,id: int):
    try:
        user = User.objects.filter( id=id,is_active=True).first()
        if not user:
            return Response({'error': 'Este usuario no existe o no se encuentra'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserDetailSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def save(request):
    try:
        username = request.data.get('username').strip()
        first_name = request.data.get('first_name').strip()
        last_name = request.data.get('last_name').strip()
        email = request.data.get('email').strip()
        role_id= request.data.get('role')
        role_object = Role.objects.get(id=role_id)

        if not role_object:
            return Response({'error': 'El rol no existe o no se encuentra'}, status=status.HTTP_404_NOT_FOUND)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'El usuario ya existe en el sistema'}, status=status.HTTP_400_BAD_REQUEST)
    
        if User.objects.filter(email=email).exists():
            return Response({'error': 'El correo ya existe en el sistema'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            is_director=True,
            role=role_object
        )
        user.set_password('mantixnwusr2024*')
        user.save()
        serializer = UserDetailSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update(request: Request):
    try:
        user_id = request.data.get("id")
        if user_id is None:
            return Response({"error": "No se proporciona el id del usuario que se va a actualizar"}, status=status.HTTP_400_BAD_REQUEST)

        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        username = request.data.get("username")
        email = request.data.get("email")
        role_id = request.data.get("role")
        password = request.data.get("password")

        user = get_object_or_404(User, id=user_id)

        # Validar que el nuevo username y email no se repitan en otros usuarios
        if username and User.objects.filter(username=username).exclude(id=user_id).exists():
            return Response({"error": f'El username "{username}" ya está en uso'}, status=status.HTTP_400_BAD_REQUEST)
        if email and User.objects.filter(email=email).exclude(id=user_id).exists():
            return Response({"error": f'El correo "{email}" ya está en uso'}, status=status.HTTP_400_BAD_REQUEST)

        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        if username is not None:
            user.username = username
        if email is not None:
            user.email = email
        if password is not None:
            user.set_password(password)  # Encriptar la nueva contraseña
        if role_id is not None:
            roleObject = get_object_or_404(Role, pk=role_id)
            user.role = roleObject
        
        user.save()
        serializer = UserDetailSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({"error": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def importUsersByExcel(request, role):
    try:
        # Obtener el archivo Excel y leerlo
        excel_base64 = request.data.get('excel_base64', None)
        if excel_base64:
            try:
                excel_bytes = base64.b64decode(excel_base64)
                excel_io = io.BytesIO(excel_bytes)
                df = pd.read_excel(excel_io, header=None)
                
                # Encontrar la fila del encabezado
                header_row_idx = None
                for i, row in df.iterrows():
                    if 'Nombre de Usuario' in row.values and 'Nombre' in row.values and 'Apellido' in row.values and 'correo' in row.values:
                        header_row_idx = i
                        break
                
                if header_row_idx is None:
                    return Response({"error": "No se encontró la fila del encabezado con las columnas esperadas"}, status=status.HTTP_400_BAD_REQUEST)
                
                # Establecer la fila del encabezado
                df.columns = df.iloc[header_row_idx]
                df = df.drop(index=list(range(0, header_row_idx + 1)))
                df.reset_index(drop=True, inplace=True)

                errors = []

                for index, row in df.iterrows():
                    # Obtener los datos del usuario desde el Excel
                    username = row['Nombre de Usuario'].strip()
                    first_name = row['Nombre'].strip()
                    last_name = row['Apellido'].strip()
                    email = row['correo'].strip()

                    # Validar que no existan usuarios con el mismo username o correo
                    if User.objects.filter(username=username).exists():
                        errors.append({'fila': index, 'columna': 'Nombre de Usuario', 'message': f'El username "{username}" ya está en uso'})
                    if User.objects.filter(email=email).exists():
                        errors.append({'fila': index, 'columna': 'correo', 'message': f'El correo "{email}" ya está en uso'})

                if errors:
                    return Response({'error': errors}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    users = []
                    # Registrar los usuarios con el rol especificado
                    for index, row in df.iterrows():
                        username = row['Nombre de Usuario'].strip()
                        first_name = row['Nombre'].strip()
                        last_name = row['Apellido'].strip()
                        email = row['correo'].strip()

                        # Crear el usuario con el rol especificado
                        role_object = None
                        if role == 'directores':
                            role_object = Role.objects.get(id=Roles.DIRECTOR.value)
                            user = User.objects.create(
                                username=username,
                                first_name=first_name,
                                last_name=last_name,
                                email=email,
                                is_director=True,
                                role=role_object
                            )
                            # user.groups.add(directores_group)
                        elif role == 'managers':
                            role_object = Role.objects.get(id=Roles.MANAGER.value)
                            user = User.objects.create(
                                username=username,
                                first_name=first_name,
                                last_name=last_name,
                                email=email,
                                is_manager=True,
                                role=role_object
                            )
                            # user.groups.add(managers_group)
                        elif role == 'tecnicos':
                            role_object = Role.objects.get(id=Roles.TECHNICAL.value)
                            user = User.objects.create(
                                username=username,
                                first_name=first_name,
                                last_name=last_name,
                                email=email,
                                role=role_object
                            )
                            # user.groups.add(tecnicos_group)
                        else:
                            return Response({"error": "El rol especificado no es válido"}, status=status.HTTP_400_BAD_REQUEST)
                        user.set_password('mantixnwusr2024*')
                        user.save()
                        users.append(user)
                        serializers = UserDetailSerializer(users, many=True)
                    return Response(serializers.data, status=status.HTTP_200_OK)
            except Exception as ex:
                return Response({"error": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"error": "No se proporcionó un excel en formato BASE64"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        return Response({"error": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)