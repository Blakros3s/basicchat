import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Room, Message


class ChatConsumer(AsyncWebsocketConsumer):
    """
    This consumer handles:
    - Connecting to a chat room
    - Receiving messages from frontend WebSocket
    - Broadcasting messages to all connected clients
    - Saving messages to the database
    """
    
    async def connect(self):
        """
        Called whenever a WebSocket client tries to connect.
        Example WebSocket URL:
            ws://localhost:8000/ws/chat/room1/
        
        Steps:
        - Extract 'room_name' from URL
        - Create a group name for Channels
        - Add this WebSocket connection to the room group
        - Accept the WebSocket (establish connection)
        - Send previous messages to the user
        """

        # Extracting room name from the URL route
        self.room_name = self.scope['url_route']['kwargs']['room_name']

        # Example: room1 → chat_room1
        self.room_group_name = f"chat_{self.room_name}"

        # Add this WebSocket connection to the group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

        # Load last 50 messages from database
        messages = await self.get_room_messages()

        # Send message history to new user
        await self.send(text_data=json.dumps({
            "type": "message_history",
            "messages": messages
        }))

        print(f"User connected to: {self.room_name}")

    
    async def disconnect(self, close_code):
        """
        Called when WebSocket disconnects.
        We simply remove the user from the room group.
        """

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        print(f"User disconnected from: {self.room_name}")


    async def receive(self, text_data):
        """
        Called when WebSocket receives data from client.
        Example incoming JSON:
            { "username": "Tilak", "message": "Hello!" }
        
        Steps:
        - Parse the JSON
        - Save message to DB
        - Broadcast message to every user in room
        """

        try:
            data = json.loads(text_data)
            message = data.get("message", "")
            username = data.get("username", "Anonymous")

            # Skip empty messages
            if not message.strip():
                return

            # Save message using sync-to-async wrapper
            saved_message = await self.save_message(username, message)

            # Send message to everyone in room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",   # event handler
                    "message": saved_message["message"],
                    "username": saved_message["username"],
                    "timestamp": saved_message["timestamp"]
                }
            )

        except Exception as e:
            print("Receive error:", e)


    async def chat_message(self, event):
        """
        Handles events sent to the group.
        Whatever we broadcast above, this method receives and sends to the client.
        """

        await self.send(text_data=json.dumps({
            "type": "chat_message",
            "message": event["message"],
            "username": event["username"],
            "timestamp": event["timestamp"]
        }))


    # ------------------------
    # DATABASE METHODS
    # ------------------------

    @database_sync_to_async
    def save_message(self, username, message):
        """
        Saves message to the database.
        Must run inside thread since Django ORM is sync.
        """

        try:
            # Get or create a User object
            user, _ = User.objects.get_or_create(username=username)

            # Get/create Room
            room, _ = Room.objects.get_or_create(name=self.room_name)

            # Store message
            msg = Message.objects.create(
                user=user,
                room=room,
                content=message
            )

            return {
                "id": msg.id,
                "username": msg.user.username,
                "message": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }

        except Exception as e:
            print("DB save error:", e)
            return {"username": username, "message": message, "timestamp": ""}


    @database_sync_to_async
    def get_room_messages(self):
        """
        Returns last 50 messages for the room.
        Useful when a new user joins.
        """

        try:
            room = Room.objects.get(name=self.room_name)
            messages = Message.objects.filter(room=room).order_by("timestamp")[:50]

            return [
                {
                    "username": msg.user.username,
                    "message": msg.content,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in messages
            ]

        except Room.DoesNotExist:
            return []
        except Exception as e:
            print("DB fetch error:", e)
            return []
