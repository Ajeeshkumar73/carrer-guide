# from django.shortcuts import render

# Create your views here.
# assistant_app/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
from google import genai

# --- Configuration ---
# Configure Gemini client (run once)
# client = genai.Client(api_key=settings.GEMINI_API_KEY)

# --- Views ---

def get_gemini_chat_session(request):
    """Initializes or retrieves the Gemini chat session."""
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    if 'gemini_chat_history' not in request.session:
        # Add a system instruction for customization
        system_instruction = "You are a concise, friendly voice assistant on a website. Keep your answers brief and conversational."
        chat_config = {"system_instruction": system_instruction}

        chat = client.chats.create(model="gemini-2.5-flash", config=chat_config)

        # Store history to maintain conversation context
        request.session['gemini_chat_history'] = chat.get_history()
        request.session.modified = True

    # Reconstruct chat object from history (or use a different storage method for scale)
    history_data = request.session.get('gemini_chat_history', [])
    chat = client.chats.create(model="gemini-2.5-flash", history=history_data)
    return chat

def home_view(request):
    """Renders the main HTML interface."""
    return render(request, 'voice.html')

@csrf_exempt # Use this for simplicity in this example; for production, use a more secure method like CSRF tokens in AJAX
def chat_api(request):
    """Handles the text input from the frontend and returns Gemini's text response."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_text = data.get('message', '').strip()

            if not user_text:
                return JsonResponse({'reply': "Please speak a command."}, status=400)

            chat_session = get_gemini_chat_session(request)

            # Send message and get response
            response = chat_session.send_message(user_text)

            # Update and save the chat history in the session
            request.session['gemini_chat_history'] = chat_session.get_history()
            request.session.modified = True

            return JsonResponse({'reply': response.text})
        except Exception as e:
            return JsonResponse({'reply': f"An error occurred: {e}"}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)