from django.db import models
from django.contrib.auth.models import User


COLOR_CHOICES = [
    ('indigo', 'Indigo'),
    ('blue', 'Blue'),
    ('purple', 'Purple'),
    ('teal', 'Teal'),
    ('emerald', 'Emerald'),
    ('rose', 'Rose'),
    ('orange', 'Orange'),
    ('red', 'Red'),
    ('green', 'Green'),
    ('pink', 'Pink'),
]


class ChatMessage(models.Model):
    """
    Model to store chat messages (the UI history).
    The 'user' ForeignKey links the message to the Django user.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    session_id = models.CharField(max_length=255, db_index=True)
    role = models.CharField(max_length=10)  # 'user' or 'agent'
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
        verbose_name_plural = "Chat Messages"
        
    def __str__(self):
        return f"[{self.session_id}] {self.role}: {self.text[:50]}..."


class AppSettings(models.Model):
    """
    Stores global, single-instance application settings for the website name,
    link, and logo. There should only ever be one record of this model.
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        primary_key=True
    )
    website_name = models.CharField(
        max_length=100, 
        default="Vick's ChatBot",
        verbose_name="Website/App Name"
    )
    website_link = models.URLField(
        max_length=255, 
        default='https://github.com/imvickykumar999/ADK-Django',
        verbose_name="Primary Website Link"
    )
    website_logo_url = models.URLField(
        max_length=255, 
        default='https://avatars.githubusercontent.com/u/67197854',
        verbose_name="Logo URL"
    )
    theme_color = models.CharField(
        max_length=20, 
        choices=COLOR_CHOICES, # Added choices
        default='indigo', 
        help_text="Select a base Tailwind color name for the application theme."
    )

    def __str__(self):
        return "Application Settings"

    def save(self, *args, **kwargs):
        # Enforce singleton pattern (only one object allowed)
        if self._state.adding and AppSettings.objects.exists():
            pass # Rely on admin/view logic to handle creation
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "App Settings"
