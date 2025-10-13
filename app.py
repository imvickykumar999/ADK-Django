import os
import tempfile
import json
from flask import Flask, request, render_template_string, jsonify
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# --- IMPORTANT SETUP ---
# Get your Groq API Key from https://console.groq.com/keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("Warning: GROQ_API_KEY not found. API calls will fail.")

# --- HTML TEMPLATE AS A PYTHON STRING ---
# This eliminates the need for a separate 'templates/index.html' file.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ursy Voice Assistant (Flask/Groq)</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        body {
            font-family: 'Inter', sans-serif;
            background-color: #0d1117; /* Dark background */
        }
        /* Removed fixed .container width for better responsiveness */
    </style>
</head>
<body class="flex items-center justify-center min-h-screen p-4">

    <div id="app" class="w-full max-w-md bg-gray-800 p-6 rounded-xl shadow-2xl border border-blue-700/50">
        <h1 class="text-3xl font-extrabold text-white mb-6 text-center">
            <span class="text-blue-400">Ursy</span> - Voice Assistant
        </h1>

        <div class="space-y-4 mb-8">
            <div id="status-box" class="p-3 rounded-lg bg-gray-700 shadow-md">
                <p id="status-text" class="text-sm font-semibold text-blue-300 transition duration-300">
                    Click the button to start talking to Ursy!
                </p>
            </div>

            <div id="user-prompt-box" class="p-3 rounded-lg bg-gray-900 shadow-inner min-h-[4rem]">
                <p class="text-xs font-bold text-gray-500 mb-1">You said:</p>
                <p id="user-prompt" class="text-base text-gray-200 italic"></p>
            </div>

            <div id="llm-response-box" class="p-3 rounded-lg bg-blue-900/30 border border-blue-500/50 shadow-lg min-h-[5rem]">
                <p class="text-xs font-bold text-blue-400 mb-1">Ursy responds:</p>
                <p id="llm-response" class="text-lg text-white font-medium"></p>
            </div>
        </div>

        <div class="flex justify-center">
            <button id="mic-button" 
                    class="w-full py-4 px-6 rounded-full font-bold text-lg 
                            bg-blue-600 hover:bg-blue-700 transition duration-300 
                            shadow-xl hover:shadow-2xl active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed text-white">
                <svg id="mic-icon" class="inline w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m8 0h-8"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                <span>Press and Hold to Talk (Max 5s)</span>
            </button>
        </div>
        
    </div>

    <script>
        // DOM elements
        const micButton = document.getElementById('mic-button');
        const statusText = document.getElementById('status-text');
        const userPromptEl = document.getElementById('user-prompt');
        const llmResponseEl = document.getElementById('llm-response');

        // State variables
        let mediaRecorder;
        let audioChunks = [];
        let isRecording = false;
        let recordingStartTime = 0; // Track when recording started
        
        // Timer for recording (matching the 5s limit in the original Python script)
        const MAX_RECORDING_DURATION = 5000; // 5 seconds
        const MIN_RECORDING_DURATION = 500; // Minimum duration for valid audio: 500ms

        // --- UI Update Functions ---
        function updateStatus(text, color = 'text-blue-300') {
            statusText.textContent = text;
            statusText.className = `text-sm font-semibold ${color} transition duration-300`;
        }

        function disableButton() {
            micButton.disabled = true;
            micButton.querySelector('span').textContent = 'Processing...';
        }

        function enableButton() {
            micButton.disabled = false;
            micButton.querySelector('span').textContent = 'Press and Hold to Talk (Max 5s)';
            updateStatus('Conversation complete. Click the button to talk again!');
        }

        // --- Audio Recording Functions (Client Side) ---

        async function startRecording() {
            if (isRecording) return;
            isRecording = true;
            audioChunks = [];
            userPromptEl.textContent = '';
            llmResponseEl.textContent = '';
            
            // Set start time immediately
            recordingStartTime = Date.now(); 

            micButton.classList.remove('bg-blue-600'); // Remove initial color
            micButton.classList.add('bg-red-600', 'animate-pulse');
            micButton.querySelector('span').textContent = 'Recording...';
            updateStatus('Listening...', 'text-red-400');

            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                // Use a common mimeType for broad compatibility
                mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' }); 

                mediaRecorder.ondataavailable = event => {
                    audioChunks.push(event.data);
                };

                mediaRecorder.onstop = () => {
                    isRecording = false;
                    micButton.classList.remove('bg-red-600', 'animate-pulse');
                    micButton.classList.add('bg-blue-600');
                    micButton.querySelector('span').textContent = 'Sending to Server...';
                    
                    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                    processAudio(audioBlob);

                    // Stop microphone stream tracks
                    stream.getTracks().forEach(track => track.stop());
                };

                mediaRecorder.start();
                
                // Set timeout to automatically stop recording after MAX_RECORDING_DURATION
                setTimeout(() => {
                    if (mediaRecorder.state === 'recording') {
                        mediaRecorder.stop();
                    }
                }, MAX_RECORDING_DURATION);

            } catch (error) {
                console.error("Microphone access failed:", error);
                updateStatus(`Error: Microphone access denied. (${error.name})`, 'text-yellow-500');
                micButton.classList.remove('bg-red-600', 'animate-pulse');
                micButton.classList.add('bg-blue-600');
                enableButton();
                isRecording = false;
            }
        }
        
        function stopRecording() {
            if (mediaRecorder && mediaRecorder.state === 'recording') {
                const elapsedTime = Date.now() - recordingStartTime;

                if (elapsedTime < MIN_RECORDING_DURATION) {
                    // Wait for the minimum duration before stopping
                    const remainingTime = MIN_RECORDING_DURATION - elapsedTime;
                    updateStatus(`Please hold for another ${Math.ceil(remainingTime)}ms...`, 'text-yellow-400');
                    
                    // Delay the stop to capture the minimum amount of audio
                    setTimeout(() => {
                        if (mediaRecorder.state === 'recording') {
                               mediaRecorder.stop();
                        }
                    }, remainingTime);

                } else {
                    // Already recorded long enough, stop immediately
                    mediaRecorder.stop();
                }
            }
        }

        // --- Server Interaction ---

        async function processAudio(audioBlob) {
            disableButton();
            updateStatus('Transcribing and Thinking...', 'text-yellow-400');

            const formData = new FormData();
            // Use 'audio_file' as the key to match the Flask backend
            formData.append('audio_file', audioBlob, 'recording.webm'); 

            try {
                const response = await fetch('/process_audio', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    // Attempt to read the error response as text, then parse the JSON error payload
                    const errorText = await response.text();
                    let errorJson;
                    try {
                        errorJson = JSON.parse(errorText);
                    } catch (e) {
                        // Fallback if the response isn't JSON (e.g., plain HTML error page)
                        throw new Error(`Server returned status ${response.status} with error: ${errorText.substring(0, 100)}...`);
                    }

                    let errorMessage = errorJson.error || `HTTP error! status: ${response.status}`;
                    
                    // Provide clearer message if Groq error is about file size
                    if (errorMessage.includes("Audio file is too short")) {
                        errorMessage = "The recorded audio was still too short. Please speak immediately after pressing the button.";
                    }
                    
                    throw new Error(errorMessage);
                }

                const data = await response.json();

                // Update UI with transcript and response
                userPromptEl.textContent = data.user_prompt;
                llmResponseEl.textContent = data.llm_response;

                // 4. Client-side TTS playback
                speak(data.llm_response);

            } catch (error) {
                console.error('Fetch/Processing Error:', error);
                llmResponseEl.textContent = `Error: ${error.message}`;
                updateStatus('A critical error occurred.', 'text-red-500');
                enableButton();
            }
        }
        
        // --- Client-Side Text-to-Speech (TTS) ---

        function speak(text) {
            updateStatus('Speaking...', 'text-green-400');
            // Check if TTS is available
            if (!('speechSynthesis' in window)) {
                console.warn('Web Speech API is not supported in this browser.');
                enableButton();
                return;
            }

            const utterance = new SpeechSynthesisUtterance(text);
            
            // Set properties if needed (optional)
            // utterance.rate = 1.0; 
            // utterance.pitch = 1.0;

            utterance.onend = () => {
                enableButton(); // Re-enable button after speaking is done
            };
            
            utterance.onerror = (event) => {
                console.error('SpeechSynthesisUtterance.onerror', event);
                // If TTS fails, still re-enable the button
                enableButton();
            };
            
            // Find a suitable voice if desired
            // window.speechSynthesis.onvoiceschanged = () => {
            //     const voices = window.speechSynthesis.getVoices();
            //     const femaleVoice = voices.find(voice => voice.name.toLowerCase().includes('female'));
            //     if (femaleVoice) {
            //         utterance.voice = femaleVoice;
            //     }
            //     speechSynthesis.speak(utterance);
            // };
            
            // If onvoiceschanged isn't reliable, just speak
            speechSynthesis.speak(utterance);
        }


        // --- Event Listener: The "Press and Hold" Logic ---
        // This setup handles both mouse (click and hold) and touch (touch and hold) gestures.
        
        // Check for microphone support on page load (optional but helpful)
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            updateStatus("Error: Your browser does not support audio recording.", 'text-red-500');
            micButton.disabled = true;
        }


        micButton.addEventListener('mousedown', startRecording);
        micButton.addEventListener('mouseup', stopRecording);
        
        // Handle touch events for mobile
        micButton.addEventListener('touchstart', (e) => {
            e.preventDefault();
            startRecording();
        });
        micButton.addEventListener('touchend', (e) => {
            e.preventDefault();
            stopRecording();
        });

    </script>
</body>
</html>
"""

# ----------------- FLASK ROUTES -----------------

@app.route('/')
def index():
    """Renders the main HTML page from the string template."""
    # Use render_template_string instead of render_template
    return render_template_string(HTML_TEMPLATE)

def get_groq_response(prompt):
    """Gets a chat completion from the Groq API."""
    if not GROQ_API_KEY:
        return "Sorry, I can't talk right now. My API key is missing on the server."
    
    client = Groq(api_key=GROQ_API_KEY)
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a friendly and helpful character in a video game named Ursy. Keep your responses concise and conversational."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.1-8b-instant"
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Groq LLM API Error: {e}")
        return "I'm having trouble connecting to my brain right now. Please try again."

@app.route('/process_audio', methods=['POST'])
def process_audio():
    """Receives audio blob, transcribes it, and generates an LLM response."""
    if 'audio_file' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    audio_file = request.files['audio_file']
    
    if not GROQ_API_KEY:
        return jsonify({"error": "Server API key is missing."}), 500

    client = Groq(api_key=GROQ_API_KEY)

    # 1. Save the received audio file temporarily
    temp_file_path = None
    try:
        # Groq Whisper API needs a file handle, so we save the incoming blob
        # Note: The original code had a small bug in suffix creation, using f".{audio_file.filename.split('.')[-1]}"
        # which fails if 'audio_file.filename' is an empty string or doesn't have an extension.
        # A safer approach for a blob named 'recording.webm' from the client is to just use a fixed suffix.
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".webm")
        audio_file.save(temp_file.name)
        temp_file_path = temp_file.name
        temp_file.close()

        # 2. Transcribe the audio file using Groq Whisper
        with open(temp_file_path, "rb") as file:
            # We pass the file as a tuple (filename, file_handle_content) for Groq's API
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(temp_file_path), file.read()),
                model="whisper-large-v3",
                response_format="json",
            )
            user_prompt = transcription.text.strip()
            
            if not user_prompt:
                return jsonify({
                    "user_prompt": "No clear speech detected.",
                    "llm_response": "I didn't quite catch that. Could you please speak up?"
                })

        # 3. Get LLM response
        llm_response = get_groq_response(user_prompt)

        return jsonify({
            "user_prompt": user_prompt,
            "llm_response": llm_response
        })

    except Exception as e:
        print(f"Server Processing Error: {e}")
        return jsonify({"error": f"An internal server error occurred: {e}"}), 500
    
    finally:
        # Clean up the temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

if __name__ == '__main__':
    # Set host='0.0.0.0' for deployment environments like Canvas
    app.run(debug=True, host='0.0.0.0')
