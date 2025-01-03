from django.contrib import admin
from .models import User, ChatRoom, Message, ChatKey

admin.site.register(User)
admin.site.register(ChatRoom)
admin.site.register(Message)
admin.site.register(ChatKey)
# Register your models here.
