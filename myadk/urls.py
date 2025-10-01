from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')),

    path('accounts/', include('django.contrib.auth.urls')),
]

# Serving static and media files during development (DEBUG=True)
if settings.DEBUG:
    # 1. Static files (for CSS, JS, etc.)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # 2. Media files (for user-uploaded content, if you implement it later)
    # Note: MEDIA_URL and MEDIA_ROOT are not defined in your settings.py yet,
    # but this is the correct structure for when you do define them.
    # If not defined, Django ignores this line.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
