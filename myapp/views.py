import asyncio
import secrets
import os
from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
from django.db.models import Max
from django.contrib.auth.decorators import login_required # Import for function-based view
# NOTE: We switch ChatAPIView to synchronous since DRF APIView dispatcher is sync by default
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google.adk.sessions import DatabaseSessionService
from google.adk.runners import Runner
from google.genai.types import Content, Part
from .models import ChatMessage
from .serializers import ChatMessageSerializer, ChatRequestSerializer

# Import the ADK Agent (Corrected path)
try:
    from myadk.wikipedia_analyst.root_agent import root_agent
except ImportError:
    print("WARNING: ADK agent not found. Chat API will be disabled.")
    root_agent = None

# --- Global ADK Initialization ---
ADK_APP_NAME = getattr(settings, 'ADK_APP_NAME', 'django_adk_chat')

# FIX: Construct the DB_URL using settings.BASE_DIR and pass it to DatabaseSessionService
DB_PATH = os.path.join(settings.BASE_DIR, 'db.sqlite3')
DB_URL = f"sqlite:///{DB_PATH}"
session_service = DatabaseSessionService(db_url=DB_URL)

runner = None
if root_agent:
    runner = Runner(
        agent=root_agent,
        app_name=ADK_APP_NAME,
        session_service=session_service,
    )

adk_sessions = {} # Tracks initialized ADK sessions in memory

def get_adk_user_id(request) -> str:
    """Returns the ADK user ID, which is the Django User ID (PK)."""
    # Use request.user.pk (Primary Key) which is guaranteed to be unique and persistent
    # We must convert it to a string for use as the ADK user_id
    if request.user.is_authenticated:
        return str(request.user.pk)
    # Fallback to an anonymous ID, though these views should be protected by @login_required
    return "anonymous_user"

# Use a synchronous wrapper for the async ADK session initialization
def initialize_adk_session_sync(session_id: str, adk_user_id: str):
    """Synchronously ensures the ADK session is accessible and created."""
    # Key the in-memory cache by both user and session ID for separation
    cache_key = f"{adk_user_id}:{session_id}"
    
    if cache_key not in adk_sessions:
        print(f"Initializing ADK session check for {adk_user_id}/{session_id}")
        
        async def _init_session():
            try:
                session = await session_service.get_session(
                    app_name=ADK_APP_NAME, 
                    user_id=adk_user_id, 
                    session_id=session_id
                )
                if not session:
                    await session_service.create_session(
                        app_name=ADK_APP_NAME,
                        user_id=adk_user_id,
                        session_id=session_id
                    )
            except Exception as e:
                print(f"DatabaseSessionService Initialization Error: {e}")
                raise 
            
            adk_sessions[cache_key] = True

        asyncio.run(_init_session())


# --- Web Page View ---
@login_required
def index(request):
    """Serves the main chat page, handling session ID redirection, protected by login."""
    session_id = request.GET.get('session_id')
    
    if not session_id:
        # Generate a new session ID and redirect
        new_session_id = secrets.token_hex(4)
        return redirect(f"{reverse('index')}?session_id={new_session_id}")
    
    return render(request, 'myapp/index.html', {
        'current_session_id': session_id
    })


# --- API Views (DRF) ---

class ChatHistoryView(APIView):
    """Retrieves chat history for the current session and all sessions, filtered by user."""
    
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
            
        adk_user_id = get_adk_user_id(request)
        current_session_id = request.GET.get('session_id')
        
        if not current_session_id:
            return Response({"history": [], "sessions": []}, status=status.HTTP_200_OK)

        # 1. Load History for the current session, FILTERED by user_id
        history_qs = ChatMessage.objects.filter(
            user_id=request.user.pk, # Filter by Django user PK
            session_id=current_session_id
        )
        history_data = ChatMessageSerializer(history_qs, many=True).data
        
        # 2. Load all unique session IDs, FILTERED by user_id
        sessions_qs = ChatMessage.objects.filter(
            user_id=request.user.pk # Filter by Django user PK
        ).values('session_id').annotate(
            max_timestamp=Max('timestamp')
        ).order_by('-max_timestamp')
        
        sessions = [item['session_id'] for item in sessions_qs]

        return Response({
            "history": history_data,
            "current_session_id": current_session_id,
            "sessions": sessions
        })


class ChatAPIView(APIView):
    """Handles new user messages and runs the ADK agent, protected and filtered by user."""

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

        adk_user_id = get_adk_user_id(request)
        
        if not runner:
            return Response({"response": "Error: Agent runner is not initialized."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user_input = serializer.validated_data['message']
        current_session_id = request.GET.get('session_id')
        
        if not current_session_id:
            return Response({"response": "Error: Session ID is missing."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Ensure the ADK session is initialized/loaded (using the synchronous wrapper)
        try:
            # Pass the user ID to the initializer
            initialize_adk_session_sync(current_session_id, adk_user_id)
        except Exception as e:
            return Response({"response": f"ADK Session Init Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 2. Save user message to Django DB, setting the user_id field
        ChatMessage.objects.create(
            user_id=request.user.pk, # Set the Foreign Key to the current user
            session_id=current_session_id, 
            role="user", 
            text=user_input
        )

        # 3. Prepare the message for the runner
        message = Content(role="user", parts=[Part(text=user_input)])

        final_response = "Sorry, I encountered an internal error."

        # 4. Define the async function to run the agent (internal to the post method)
        async def get_agent_response(msg, session_id, user_id):
            response = ""
            async for event in runner.run_async(
                user_id=user_id, # Use the dynamic ADK user ID here
                session_id=session_id,
                new_message=msg
            ):
                if hasattr(event, "is_final_response") and event.is_final_response():
                    if hasattr(event.content, "parts") and event.content.parts:
                        response = event.content.parts[0].text
                        break
            return response

        # 5. Run the ADK Agent asynchronously from the synchronous view
        try:
            final_response = asyncio.run(get_agent_response(message, current_session_id, adk_user_id))
        except Exception as e:
            final_response = f"An agent error occurred during run: {str(e)}"
            return Response({"response": final_response}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # 6. Save agent message to Django DB, setting the user_id field
        ChatMessage.objects.create(
            user_id=request.user.pk, # Set the Foreign Key to the current user
            session_id=current_session_id, 
            role="agent", 
            text=final_response
        )

        return Response({"response": final_response}, status=status.HTTP_200_OK)
