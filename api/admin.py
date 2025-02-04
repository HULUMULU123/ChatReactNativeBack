from django.contrib import admin
from .models import User, ChatRoom, Message, ChatKey, Reaction, GroupChat, GroupMessage

admin.site.register(User)
admin.site.register(ChatRoom)
admin.site.register(Message)
admin.site.register(ChatKey)
admin.site.register(Reaction)
admin.site.register(GroupMessage)
admin.site.register(GroupChat)
# Register your models here.
