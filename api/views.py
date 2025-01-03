from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from django.contrib.auth import authenticate

from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer,SignUpSerializer
from .models import User

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
def get_auth_for_user(user):
    tokens = RefreshToken.for_user(user)
    print('token', tokens)
    return {
        'user': UserSerializer(user).data,
        'tokens': {
            'access': str(tokens.access_token),
            'refresh': str(tokens)
        }
    }


class SignView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response(status=400)
        print(username, password)
        user = authenticate(username=username, password=password)
        print(User.objects.get(username=username).password, 'testing')
        if not user:
            return Response(status=401)
        
        user_data = get_auth_for_user(user)
        print(user_data)
        return Response(user_data)


class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        )
        public_key = private_key.public_key()

        # Сохранение приватного ключа
        private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
        )

        # Сохранение публичного ключа
        public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        print('test-key', private_pem.decode('utf-8'), public_pem.decode('utf-8'), request.data)
        request.data.update([('private_key', private_pem.decode('utf-8')), ('public_key', public_pem.decode('utf-8'))])
        print(request.data)
        new_user = SignUpSerializer(data=request.data)
        new_user.is_valid(raise_exception=True)
        user = new_user.save()

        user_data = get_auth_for_user(user)
        
        return Response(user_data)
        
# Create your views here.
