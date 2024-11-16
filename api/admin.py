from django.contrib import admin
from .models import User, ChatRoom, Message

admin.site.register(User)
admin.site.register(ChatRoom)
admin.site.register(Message)
# Register your models here.
