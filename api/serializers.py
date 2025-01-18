from rest_framework import serializers
from .models import User, Message, ChatRoom, ChatKey

class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'password',
            'first_name',
            'last_name',
            'public_key',
            'private_key',
        ]
        extra_kwargs = {
            'last_name': {
                # Ensures that when serializing, this field will be xcluded
                'write_only': True
            },
            'first_name': {
                # Ensures that when serializing, this field will be xcluded
                'write_only': True
            },
            'password': {
                # Ensures that when serializing, this field will be xcluded
                'write_only': True
            },
            'private_key': {
                'write_only': True
            },
            'public_key': {
                'write_only': True
            }
        }
    def create(self, validated_data):
        
        print(validated_data, 'lookondata')
        # Clean all values, set as lowercase
        username = validated_data['username'].lower()
        last_name = validated_data['last_name'].lower()
        first_name = validated_data['first_name'].lower()
        # Create a new user
        private_key = validated_data['private_key']
        public_key = validated_data['public_key']
        print(public_key)
        user = User(
            username=username,
            private_key=private_key,
            public_key=public_key,
            first_name=first_name,
            last_name=last_name,
        )
        password = validated_data['password']
        
        user.set_password(password)
        user.save()
        return user



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'thumbnail',
            'private_key',
            'online',
        ]

class AvatarSerializer(UserSerializer):
    class Meta: 
        model = User
        fields = ['username','thumbnail']
class SearchSerializer(UserSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'username',
            'status',
            'thumbnail'
        ]
    def get_status(self, obj):
        return obj.online
    
class MessageSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    class Meta:
        model = Message
        fields = '__all__'

    def get_username(self, obj):
        return obj.sender.username
    
class ChatsSerializer(serializers.ModelSerializer):
    chat_name = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unreaded_messages = serializers.SerializerMethodField()
    online = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    key = serializers.SerializerMethodField()
    class Meta:
        model = ChatRoom
        fields = ['chat_name',
                    'last_message',
                    'unreaded_messages',
                    'online',
                    'avatar',
                    'key']
    

    def get_chat_name(self, obj:ChatRoom):
        if obj.participants.count() == 2 and obj.name is None:
            current_user = self.context.get('user_name')
            print(current_user)
            print('========')
            print(obj.participants)
            participants = obj.participants.exclude(username=current_user)
            return participants.first().username
            
        else: 
            return obj.name
        
    def get_last_message(self, obj:ChatRoom):
        last_message = Message.objects.filter(room=obj).last()
        message = {
            "content": last_message.content if last_message else None,
            "created_at": str(last_message.created_at) if last_message else None,
            'from': last_message.sender.username if last_message else None,
        }
        return message
    
    def get_unreaded_messages(self, obj:ChatRoom):
        current_user = self.context.get('user_name')
        messages_count = Message.objects.filter(room=obj, is_read=False).exclude(sender__username=current_user).count()
        return messages_count
    
    def get_online(self, obj):
        online = self.context.get('user_online')
        return online
    def get_avatar(self, obj:ChatRoom):
        participants = obj.participants
        current_username = self.context.get('user_name')
        current_user = User.objects.get(username=current_username)
        if participants.count() == 2:
            second_participant = participants.exclude(id=current_user.id).first()
        avatar = second_participant.thumbnail.url
        return avatar
    
    def get_key(self, obj):
        participants = obj.participants
        current_username = self.context.get('user_name')
        current_user = User.objects.get(username=current_username)
        if participants.count() == 2:
            second_participant = participants.exclude(id=current_user.id).first()
        chat_keys = ChatKey.get_chat_keys(current_user, second_participant)
        if current_username == chat_keys.username1:
            user_chat_key = chat_keys.user_key_1
        else:
            user_chat_key = chat_keys.user_key_2
        return user_chat_key