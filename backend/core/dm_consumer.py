import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import DirectMessage


class DirectMessageConsumer(AsyncWebsocketConsumer):
    """
    Consumer for handling 1-on-1 direct messages between users.
    WebSocket URL: ws://localhost:8000/ws/dm/<recipient_username>/
    """
    
    async def connect(self):
        """
        Called when WebSocket connection is established.
        Creates a unique room for the two users (sorted alphabetically for consistency).
        """
        # Get current user's username from query params
        query_string = self.scope.get('query_string', b'').decode()
        query_params = dict(param.split('=') for param in query_string.split('&') if '=' in param)
        self.current_username = query_params.get('user', 'anonymous')
        
        # Get recipient username from URL
        self.recipient_username = self.scope['url_route']['kwargs']['username']
        
        # Create unique room name (sorted to ensure same room for both users)
        users = sorted([self.current_username, self.recipient_username])
        self.room_name = f"dm_{users[0]}_{users[1]}"
        self.room_group_name = f"chat_{self.room_name}"
        
        # Add to channel group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Accept connection
        await self.accept()
        
        # Load conversation history
        messages = await self.get_conversation_history()
        
        # Send message history
        await self.send(text_data=json.dumps({
            "type": "message_history",
            "messages": messages
        }))
        
        print(f"DM connection: {self.current_username} <-> {self.recipient_username}")
    
    
    async def disconnect(self, close_code):
        """Remove from channel group on disconnect"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"DM disconnected: {self.current_username} <-> {self.recipient_username}")
    
    
    async def receive(self, text_data):
        """
        Receive message from WebSocket and broadcast to recipient
        """
        try:
            data = json.loads(text_data)
            message = data.get("message", "")
            sender_username = data.get("username", self.current_username)
            
            if not message.strip():
                return
            
            # Save DM to database
            saved_message = await self.save_direct_message(
                sender_username, 
                self.recipient_username, 
                message
            )
            
            # Broadcast to both users in the DM room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": saved_message["message"],
                    "username": saved_message["username"],
                    "timestamp": saved_message["timestamp"],
                    "is_dm": True
                }
            )
            
        except Exception as e:
            print(f"DM receive error: {e}")
    
    
    async def chat_message(self, event):
        """Send message to WebSocket"""
        await self.send(text_data=json.dumps({
            "type": "chat_message",
            "message": event["message"],
            "username": event["username"],
            "timestamp": event["timestamp"],
            "is_dm": event.get("is_dm", True)
        }))
    
    
    @database_sync_to_async
    def save_direct_message(self, sender_username, recipient_username, message):
        """Save direct message to database"""
        try:
            sender, _ = User.objects.get_or_create(username=sender_username)
            recipient, _ = User.objects.get_or_create(username=recipient_username)
            
            dm = DirectMessage.objects.create(
                sender=sender,
                recipient=recipient,
                content=message
            )
            
            return {
                "id": dm.id,
                "username": dm.sender.username,
                "message": dm.content,
                "timestamp": dm.timestamp.isoformat()
            }
        except Exception as e:
            print(f"DB save error: {e}")
            return {
                "username": sender_username, 
                "message": message, 
                "timestamp": ""
            }
    
    
    @database_sync_to_async
    def get_conversation_history(self):
        """Get last 50 messages between the two users"""
        try:
            sender = User.objects.get(username=self.current_username)
            recipient = User.objects.get(username=self.recipient_username)
            
            messages = DirectMessage.get_conversation(sender, recipient)[:50]
            
            return [
                {
                    "username": msg.sender.username,
                    "message": msg.content,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in messages
            ]
        except User.DoesNotExist:
            return []
        except Exception as e:
            print(f"DB fetch error: {e}")
            return []
