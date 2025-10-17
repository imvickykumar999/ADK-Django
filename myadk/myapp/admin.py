from django.contrib import admin
from .models import ChatMessage, AppSettings
from django.utils.html import format_html


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


@admin.register(AppSettings)
class AppSettingsAdmin(admin.ModelAdmin):
    """
    Custom admin interface for the singleton AppSettings model.
    Displays the logo as a clickable image and restricts object creation/deletion.
    """
    # Fields to display in the list view (UPDATED to include 'user')
    list_display = ('user', 'website_name', 'website_link', 'logo_display', 'theme_color')
    
    # All fields should be editable (UPDATED with theme_color)
    fieldsets = (
        (None, {
            'fields': ('website_name', 'website_link', 'website_logo_url', 'theme_color')
        }),
    )

    # --- Custom Method for Logo Image Display ---
    @admin.display(description='Logo Image')
    def logo_display(self, obj):
        """Renders the website logo URL as a clickable image link."""
        if obj.website_logo_url and obj.website_link:
            # Use format_html to securely generate the anchor and image tags
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="max-height: 50px; max-width: 100px; border-radius: 5px; object-fit: cover;" alt="App Logo" /></a>',
                obj.website_link,
                obj.website_logo_url
            )
        return "No Logo Available"
    
    # Enforce singleton behavior: Check if an object exists
    def has_add_permission(self, request):
        """Disables the 'Add' button if an AppSettings object already exists."""
        # Note: Since the model is keyed by user (primary_key=True on the OneToOneField),
        # this check might be inaccurate for a multi-user setup where each user gets one setting.
        # However, following the original logic:
        return not AppSettings.objects.exists()
    
    # Prevent deletion of the single configuration object
    def has_delete_permission(self, request, obj=None):
        """Prevents the deletion of the single AppSettings object."""
        return False
