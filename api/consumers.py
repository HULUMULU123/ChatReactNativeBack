import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import User, ChatRoom, Message, ChatKey
from django.db.models import Q, Max
from .serializers import SearchSerializer, MessageSerializer, ChatsSerializer

import base64
from django.core.files.base import ContentFile
class ChatConsumer(WebsocketConsumer):

    def connect(self):
        user = self.scope['user']
        print(user.username, 'testing consumer')
        if not user:
            return
        # Save username
        
        self.username = user.username
        self.groups.append(self.username)
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
        if data_source == 'send_message':
            print('insede origin msg')
            self.receive_message(data)
        elif data_source == 'get_chat':
            
            self.receive_chat(data)
        if data_source == 'index':
            print('inside index')
            self.receive_all_chats()

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
        
        print(serialized.data, self.channel_name)
        # Send search results back to the user
        self.send_group(self.username, 'search', serialized.data)

    def receive_message(self, data):
        print(data)
        
        

        
        chat = ChatRoom.get_private_chat(data['from'], data['to'])
        print(chat, 'chek')
        
        message_text = data['msg']['text']
        file_url = data['msg'].get('file')
        print(file_url)
        print(data)
        if len(file_url) > 0: 
            message = Message.objects.create(room=chat, sender=User.objects.get(username=data['from']), content=message_text, file=file_url)
        else:
            message = Message.objects.create(room=chat, sender=User.objects.get(username=data['from']), content=message_text, file='')
        message.save()
        print('inside msg')
        response = {
            
            'source': 'chat',
            'content': message_text,
            'file': file_url,
            'created_at': str(message.created_at),
            'from': data['from'],
            'to': data['to'],
            'sender': self.channel_name
        }

        # -------------------------------------------------------------------------
        # res = {
        #     'type' : 'send_message',
        #     'data': response

        # }
        # async_to_sync(self.channel_layer.group_send)(data['to'], res)
        self.send_group(data['to'], 'chat_message', response)

    def receive_chat(self, data):
        chat = ChatRoom.get_private_chat(data['user1'], data['user2'])
        chat_keys = ChatKey.get_chat_keys(data['user1'], data['user2'])
        print(chat_keys)
        messages = Message.objects.filter(room=chat, is_read=False).exclude(sender__username=self.username)
        messages.update(is_read=True)
        messages = Message.objects.filter(room=chat)
        

        serialized = MessageSerializer(messages, many=True)
        
        if self.username == chat_keys.username1:
            user_chat_key = chat_keys.user_key_1
        else:
            user_chat_key = chat_keys.user_key_2
        
        print(serialized.data)
        response = {
            'type': 'get_chat',
            'data': serialized.data,
            'chat_key': user_chat_key,
        }

        
        self.send_group(data['user1'], 'get_chat', response)
    
    def receive_all_chats(self):
        user =  User.objects.get(username=self.username)
        user_id = user.id
        user_online = user.online
        
        chats = ChatRoom.objects.filter(participants=user_id)
        chats = chats.annotate(last_message_date=Max('messages__created_at')).order_by('-last_message_date')
        serialized = ChatsSerializer(chats, many=True, context={'user_name': self.username, "user_online": user_online })
        print(serialized.data, 'online')
        response = {
            'type': 'all_chats',
            'data': serialized.data
        }
        
        self.send_group(self.username, 'get_all_chats', response)


    # def chat_message(self, data):
    #     response = {
    #         'type': 'chat_message',
    #         'msg': data['msg'],
    #         'from': data['from'],
    #         'to': data['to'],
    #     }
        

    #     async_to_sync(self.send)(response)
    # --------------------------------------------------------------------------------
    # Catch/all broadcast to client helpers
    # -------------------------------------------------------------------------------
    def send_group(self, group, source, data):
        
        response = {
            'type': 'broadcast_group',
            'source': source,
            'data': data
        }
        print(group, data, '123', self.groups)
        
        async_to_sync(self.channel_layer.group_send)(group, response)

    
    def broadcast_group(self, data):
        # if data['source'] == 'chat_message':
        #     if data['data']['to'] == self.scope['user'].username:
        #         print(f"data['data']['from']: {data['data']['from']}")
        #         print(f"self.scope['user'].username: {self.scope['user'].username}")
        #         print(f"Handling broadcast for: {self.channel_name} with data: {data}")
        #         self.send(text_data=json.dumps(data))
        # else:
            '''
            data: 
                - type: 'broadcast-group'
                - source: where it originated from
                - data: what ever want to send as a dict
            '''
            # data.pop('type')

            '''
            return data: 
                - source: where it originated from
                - data: what ever want to send as a dict
            '''
            print('uuu321', data)
            print(f"Handling broadcast for: {self.channel_name} with data: {data}")
            self.send(text_data=json.dumps(data))

    def send_message(self, data):
        print(data)