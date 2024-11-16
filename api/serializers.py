from rest_framework import serializers
from .models import User, Message

class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'password',
        ]
        extra_kwargs = {
            'password': {
                # Ensures that when serializing, this field will be xcluded
                'write_only': True
            }
        }
    def create(self, validated_data):
        # Clean all values, set as lowercase
        username = validated_data['username'].lower()
        # Create a new user
        user = User(
            username=username
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
            'thumbnail'
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