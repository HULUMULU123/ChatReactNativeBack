from rest_framework import serializers
from .models import User, Message, ChatRoom

class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'password',
            'public_key',
            'private_key',
        ]
        extra_kwargs = {
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
        print(validated_data)
        # Clean all values, set as lowercase
        username = validated_data['username'].lower()
        # Create a new user
        private_key = validated_data['private_key']
        public_key = validated_data['public_key']
        print(public_key)
        user = User(
            username=username,
            private_key=private_key,
            public_key=public_key
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
            'thumbnail',
            'private_key',
        ]

class SearchSerializer(UserSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'username',
            'status'
        ]
    def get_status(self, obj):
        return 'no conn'
    
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
    class Meta:
        model = ChatRoom
        fields = ['chat_name',
                    'last_message']
    
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