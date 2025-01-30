from django.contrib import admin
from .models import User, ChatRoom, Message, ChatKey, Reaction

admin.site.register(User)
admin.site.register(ChatRoom)
admin.site.register(Message)
admin.site.register(ChatKey)
admin.site.register(Reaction)
# Register your models here.
