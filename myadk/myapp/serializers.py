from rest_framework import serializers
from .models import ChatMessage, AppSettings

class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for displaying chat history."""
    class Meta:
        model = ChatMessage
        fields = ['role', 'text', 'timestamp']

class ChatRequestSerializer(serializers.Serializer):
    """Serializer for validating incoming chat POST request."""
    message = serializers.CharField(max_length=2048)

class AppSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppSettings
        # 'user' field is excluded as it's automatically handled by the view based on request.user
        fields = ['website_name', 'website_link', 'website_logo_url', 'theme_color']
        read_only_fields = [] 
