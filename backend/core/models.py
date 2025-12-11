
from django.db import models
from django.contrib.auth.models import User


class Room(models.Model):
    """Chat room model for group conversations"""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(User, related_name='chat_rooms', blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def member_count(self):
        return self.members.count()


class Message(models.Model):
    """Message model for group chat messages"""
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f'{self.user.username}: {self.content[:50]}'


class DirectMessage(models.Model):
    """Direct message model for 1-on-1 private conversations"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_dms')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_dms')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['sender', 'recipient', 'timestamp']),
        ]
    
    def __str__(self):
        return f'{self.sender.username} -> {self.recipient.username}: {self.content[:50]}'
    
    @staticmethod
    def get_conversation(user1, user2):
        """Get all messages between two users"""
        return DirectMessage.objects.filter(
            models.Q(sender=user1, recipient=user2) | 
            models.Q(sender=user2, recipient=user1)
        ).order_by('timestamp')
