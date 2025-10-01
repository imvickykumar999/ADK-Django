from rest_framework import serializers
from .models import ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for displaying chat history."""
    class Meta:
        model = ChatMessage
        fields = ['role', 'text', 'timestamp']

class ChatRequestSerializer(serializers.Serializer):
    """Serializer for validating incoming chat POST request."""
    message = serializers.CharField(max_length=2048)
