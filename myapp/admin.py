from django.contrib import admin
from .models import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """
    Custom admin interface for the ChatMessage model. 
    Provides detailed list display, filtering, and searching capabilities.
    """
    
    # 1. Fields displayed in the list view (changelist)
    list_display = (
        'id', 
        'user_display_name',  # Custom method to show username/email
        'session_id', 
        'role', 
        'text_snippet',      # Custom method for short message preview
        'timestamp',
    )

    # 2. Fields that can be used to filter the list view
    list_filter = (
        'user',              # Filter messages by the user who created them
        'role',              # Filter by 'user' or 'agent'
        'timestamp',         # Filter by date/time
    )

    # 3. Fields that allow searching in the list view
    search_fields = (
        'user__username',    # Search by the user's username
        'session_id', 
        'text',              # Search within the message content
    )
    
    # 4. Fields to use as links to the change form
    list_display_links = (
        'id', 
        'text_snippet'
    )

    # 5. Fields to be read-only in the detailed change form
    readonly_fields = (
        'user', 
        'session_id', 
        'role', 
        'timestamp'
    )
    
    # 6. Grouping fields in the change form
    fieldsets = (
        (None, {
            'fields': ('user', 'session_id', 'role', 'text')
        }),
        ('Metadata', {
            'fields': ('timestamp',),
            'classes': ('collapse',),  # Collapsible section
        })
    )
    
    # --- Custom Methods for List Display ---
    
    @admin.display(description='User')
    def user_display_name(self, obj):
        """Displays the username or a fallback for the linked user."""
        return obj.user.username if obj.user else 'N/A'
    
    @admin.display(description='Message Snippet')
    def text_snippet(self, obj):
        """Returns a truncated version of the message text for list display."""
        return obj.text[:80] + '...' if len(obj.text) > 80 else obj.text
