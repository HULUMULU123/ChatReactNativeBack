from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from django.contrib.auth import authenticate

from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer,SignUpSerializer
from .models import User

from django.http import JsonResponse
from io import BytesIO
from django.core.files.base import ContentFile
import base64

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

class UpdateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        # username = request.data.get('username')
        base64_image = request.data.get('avatar')
        type_param = request.data.get('type')
        info = request.data.get('info')
        username = request.data.get('username')

        if type_param == "avatar":
            if not base64_image:
                return JsonResponse({'error': 'Нет изображения'}, status=400)

            try:
                # Разделяем строку Base64 от префикса, если он есть
            

                # Декодируем строку Base64
                image_data = base64.b64decode(base64_image)
                
                image_file = BytesIO(image_data)
                
                # Создаем ContentFile для хранения изображения
                content_file = ContentFile(image_data, name=f"{username}_avatar.jpg")
                print(content_file)
                # Сохраняем изображение в поле модели
                user_profile = User.objects.get(username=username)
                user_profile.thumbnail.save(content_file.name, content_file, save=True)

                return JsonResponse({'message': 'Фото успешно загружено'})
            
            except Exception as e:
                return JsonResponse({'error': f'Ошибка при обработке изображения: {str(e)}'}, status=400)
        if info:
            if type_param == 'username':
                users = User.objects.filter(username=info)
                if len(users) == 0:
                    User.objects.filter(username=username).update(username=info)
                    return JsonResponse({'message': 'Success'})
                else:
                    return JsonResponse({'error': 'User already exist012'}, status=400)
            if type_param == 'name':
                User.objects.filter(username=username).update(first_name=info)
                return JsonResponse({'message': 'Success'})
            if type_param == 'surname':
                User.objects.filter(username=username).update(last_name=info)
                return JsonResponse({'message': 'Success'})
        else:
            return JsonResponse({'error': '(('}, status=400)


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
        User.objects.filter(username=username).update(online=True)
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
        
        request.data.update([('private_key', private_pem.decode('utf-8')), ('public_key', public_pem.decode('utf-8'))])
        print(request.data, 'DATATOSER')
        new_user = SignUpSerializer(data=request.data)
        new_user.is_valid(raise_exception=True)
        user = new_user.save()

        user_data = get_auth_for_user(user)
        
        return Response(user_data)
        
# Create your views here.
