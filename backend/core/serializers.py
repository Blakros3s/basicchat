from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Room, Message, DirectMessage


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'username', 'content', 'timestamp']
        read_only_fields = ['timestamp']


class DirectMessageSerializer(serializers.ModelSerializer):
    """Serializer for DirectMessage model"""
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    recipient_username = serializers.CharField(source='recipient.username', read_only=True)
    
    class Meta:
        model = DirectMessage
        fields = ['id', 'sender_username', 'recipient_username', 'content', 'timestamp', 'is_read']
        read_only_fields = ['timestamp']


class RoomSerializer(serializers.ModelSerializer):
    """Serializer for Room model"""
    message_count = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Room
        fields = ['id', 'name', 'description', 'created_at', 'message_count', 'member_count', 'last_message']
        read_only_fields = ['created_at']
    
    def get_message_count(self, obj):
        return obj.messages.count()
    
    def get_member_count(self, obj):
        return obj.members.count()
    
    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return {
                'username': last_msg.user.username,
                'content': last_msg.content,
                'timestamp': last_msg.timestamp
            }
        return None
