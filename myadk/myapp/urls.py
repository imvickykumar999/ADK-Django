from django.urls import path
from . import views

urlpatterns = [
    # Web Page Route
    path('', views.index, name='index'), 
    
    # API Routes
    path('api/history/', views.ChatHistoryView.as_view(), name='api_history'),
    path('api/chat/', views.ChatAPIView.as_view(), name='api_chat'), 
    path('api/settings/', views.AppSettingsAPIView.as_view(), name='app_settings_api'),
]
