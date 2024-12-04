from django.db import models
from django.contrib.auth.models import AbstractUser


def upload_thumbnail(instance, filename):
    path = f'thumbnails/{instance.username}'
    extension = filename.split('.')[-1]
    if extension:
        path += '.'+extension
    return path

class User(AbstractUser):
    thumbnail = models.ImageField(
        upload_to=upload_thumbnail,
        null=True,
        blank=True
    )

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

class Message(models.Model):

    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    is_read = models.BooleanField(default=False)

    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"Message {self.id} from {self.sender.username}"
    
# Create your models here.
