from django.db import models
from django.contrib.auth.models import AbstractUser
import secrets
import base64
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_public_key

import random
from PIL import Image, ImageDraw, ImageFont
import os
from io import BytesIO
from django.core.files.base import ContentFile
def upload_thumbnail(instance, filename):
    path = f'thumbnails/{instance.username}'
    extension = filename.split('.')[-1]
    if extension:
        path += '.'+extension
    return path

def generate_avatar(first_name, last_name, size=(200, 200), font_size=80):
    # Создаем рандомный цвет фона
    background_color = tuple(random.randint(0, 255) for _ in range(3))  # RGB
    text_color = (255, 255, 255)  # Белый текст

    # Берем первые буквы имени и фамилии
    initials = f"{first_name[0].upper()}{last_name[0].upper()}"

    # Создаем изображение
    img = Image.new("RGB", size, background_color)
    draw = ImageDraw.Draw(img)

    # Определяем шрифт (укажите путь к ttf-шрифту)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Linux
    if not os.path.exists(font_path):
        font_path = "C:\\Windows\\Fonts\\arial.ttf"  # Windows (проверьте наличие файла)

    font = ImageFont.truetype(font_path, font_size)

    # Рассчитываем координаты для центрирования текста
    bbox = draw.textbbox((0, 0), initials, font=font)  # Получаем координаты текста
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Центрирование текста (добавляем коррекцию вертикального смещения)
    text_x = (size[0] - text_width) // 2
    text_y = (size[1] - text_height) // 2 - bbox[1] // 2

    # Рисуем текст
    draw.text((text_x, text_y), initials, fill=text_color, font=font)

    # Сохраняем изображение в память
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue(), name=f"{first_name}_{last_name}_avatar.png")

class User(AbstractUser):
    thumbnail = models.ImageField(
        upload_to=upload_thumbnail,
        null=True,
        blank=True
    )
    public_key = models.TextField()
    private_key = models.TextField()
    online = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Если аватарки нет, создаем ее
        if not self.thumbnail:
            self.thumbnail = generate_avatar(self.first_name, self.last_name)
        super().save(*args, **kwargs)


class ChatRoom(models.Model):
    is_private = models.BooleanField(default=True)

    participants = models.ManyToManyField(User, related_name='chat_rooms')

    name = models.CharField(max_length=35, blank=True, null=True)

    group = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.is_private:
            usernames = ', '.join([user.username for user in self.participants.all()])
            return f"Private Chat: {usernames}"
        return self.name or f"Room {self.id}"

    @staticmethod
    def get_private_chat(username1, username2):
        print(username1, username2)
        user1 = User.objects.get(username=username1)
        user2 = User.objects.get(username=username2)
        '''Get or create room form two users'''
        chat = ChatRoom.objects.filter(
            is_private=True,
            participants=user1
        ).filter(participants=user2).first()
        
        if not chat:
            chat = ChatRoom.objects.create(is_private=True)
            chat.participants.add(user1, user2)

        return chat
    
class ChatKey(models.Model):
    chat = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    username1 = models.CharField(max_length=100)
    user_key_1 = models.TextField()
    username2 = models.CharField(max_length=100)
    user_key_2 = models.TextField()

    @staticmethod
    def get_chat_keys(username1, username2):

        def encrypt_chat_key_for_user(chat_key, user_public_key_pem):
            # Загрузка публичного ключа из PEM-формата
            public_key = load_pem_public_key(user_public_key_pem.encode('utf-8'))

            # Шифрование симметричного ключа
            encrypted_key = public_key.encrypt(
                base64.b64decode(chat_key),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return base64.b64encode(encrypted_key).decode('utf-8')

        user1 = User.objects.get(username=username1)
        user2 = User.objects.get(username=username2)
        chat = ChatRoom.objects.filter(
            is_private=True,
            participants=user1
        ).filter(participants=user2).first()
        chat_keys = ChatKey.objects.filter(chat=chat).first()
        if not chat_keys and chat:
            key = secrets.token_bytes(32)
            encoded_key = base64.b64encode(key).decode('utf-8')
            user_key_1 = encrypt_chat_key_for_user(encoded_key, user1.public_key)
            user_key_2 = encrypt_chat_key_for_user(encoded_key, user2.public_key)
            print('----------------------')
            print(key)
            print(user_key_1)
            print('-----------------------')
            chat_keys = ChatKey.objects.create(chat=chat, username1=user1.username, user_key_1=user_key_1, username2=user2.username, user_key_2=user_key_2)
            
        return chat_keys

class Message(models.Model):

    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    
    reply = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    content = models.TextField()
    file = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True)

    is_read = models.BooleanField(default=False)

    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"Message {self.id} from {self.sender.username}"

class Reaction(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='reactions'
    )
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE,
        related_name='reactions'
    )
    REACTION_CHOICES = [
        ("❤️", "Heart"),
        ("👍", "Thumbs Up"),
        ("💪", "strong"),
        ("👎", "Thumbs Down"),
        ("😭", "Cry"),
    ]
    emoji = models.CharField(max_length=2, choices=REACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ("user", "message")  # 1 пользователь — 1 реакция на сообщение

    def __str__(self):
        return f"{self.user} reacted {self.emoji} to Message {self.message.id}"
# Create your models here.
