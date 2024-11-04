import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import User
from django.db.models import Q
from .serializers import SearchSerializer
class ChatConsumer(WebsocketConsumer):

    def connect(self):
        user = self.scope['user']
        print(user.username, 'testing consumer')
        if not user:
            return
        # Save username
        self.username = user.username

        # Join this user to a group with their username
        async_to_sync(self.channel_layer.group_add)(self.username, self.channel_name)

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.username, self.channel_name)

    # ----------------------------------------------------------------------------------
    # Handle requests
    # ---------------------------------------------------------------------------------

    def receive(self, text_data=None):
        # Recieve message from websocket
        data = json.loads(text_data)
        data_source = data.get('source')
        # Pretty print python dict

        print('recieve', json.dumps(data, indent=2))


        # Search / filter users
        if data_source == 'search':
            self.receive_search(data)

    def receive_search(self, data):
        query = data.get('query')

        users = User.objects.filter(
            Q(username__istartswith=query) |
            Q(first_name__istartswith=query) |
            Q(last_name__istartswith=query) 
        ).exclude(
            username=self.username)
        # .annotate(
        #     pending_them=Exists(
        #         Connection
        #     )
        #     pending_me=...
        #     connected=...
        # )

        serialized = SearchSerializer(users, many=True)
        print(serialized.data)
        # Send search results back to the user
        self.send_group(self.username, 'search', serialized.data)
    # --------------------------------------------------------------------------------
    # Catch/all broadcast to client helpers
    # -------------------------------------------------------------------------------
    def send_group(self, group, source, data):
        response = {
            'type': 'broadcast_group',
            'source': source,
            'data': data
        }
        async_to_sync(self.channel_layer.group_send)(group, response)

    
    def broadcast_group(self, data):
        '''
        data: 
            - type: 'broadcast-group'
            - source: where it originated from
            - data: what ever want to send as a dict
        '''
        data.pop('type')

        '''
        return data: 
            - source: where it originated from
            - data: what ever want to send as a dict
        '''
        self.send(text_data=json.dumps(data))