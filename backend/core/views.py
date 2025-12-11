from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Room, Message, DirectMessage
from .serializers import RoomSerializer, MessageSerializer, UserSerializer, DirectMessageSerializer


class RoomViewSet(viewsets.ModelViewSet):
    """ViewSet for Room CRUD operations"""
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get all messages for a specific room"""
        room = self.get_object()
        messages = Message.objects.filter(room=room).order_by('timestamp')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def create_or_get(self, request):
        """Create a new room or get existing one"""
        room_name = request.data.get('name')
        description = request.data.get('description', '')
        
        if not room_name:
            return Response(
                {'error': 'Room name is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        room, created = Room.objects.get_or_create(
            name=room_name,
            defaults={'description': description}
        )
        serializer = self.get_serializer(room)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Message read operations"""
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    
    def get_queryset(self):
        """Filter messages by room if room_id is provided"""
        queryset = Message.objects.all()
        room_id = self.request.query_params.get('room_id', None)
        if room_id:
            queryset = queryset.filter(room_id=room_id)
        return queryset.order_by('timestamp')


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for User read operations"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search users by username"""
        query = request.query_params.get('q', '').strip()
        
        if not query:
            return Response({'users': []})
        
        users = User.objects.filter(username__icontains=query)[:20]
        serializer = self.get_serializer(users, many=True)
        return Response({'users': serializer.data})


class DirectMessageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for DirectMessage read operations"""
    queryset = DirectMessage.objects.all()
    serializer_class = DirectMessageSerializer
    
    @action(detail=False, methods=['get'])
    def conversation(self, request):
        """Get conversation between two users"""
        user1_name = request.query_params.get('user1')
        user2_name = request.query_params.get('user2')
        
        if not user1_name or not user2_name:
            return Response(
                {'error': 'Both user1 and user2 parameters required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user1 = User.objects.get(username=user1_name)
            user2 = User.objects.get(username=user2_name)
            
            messages = DirectMessage.get_conversation(user1, user2)
            serializer = self.get_serializer(messages, many=True)
            return Response({'messages': serializer.data})
        
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
