from django.db import models
from django.contrib.auth.models import User # <-- MUST BE PRESENT

class ChatMessage(models.Model):
    """
    Model to store chat messages (the UI history).
    The 'user' ForeignKey links the message to the Django user.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages') # <-- NEW/UPDATED FIELD
    session_id = models.CharField(max_length=255, db_index=True)
    role = models.CharField(max_length=10)  # 'user' or 'agent'
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
        verbose_name_plural = "Chat Messages"
        
    def __str__(self):
        return f"[{self.session_id}] {self.role}: {self.text[:50]}..."
