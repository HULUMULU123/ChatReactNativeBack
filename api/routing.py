from django.urls import path 

from . import consumers

websocket_urlpatterns = [
    path('chat/', consumers.ChatConsumer.as_asgi()),
    path('call/', consumers.CallConsumer.as_asgi())
]