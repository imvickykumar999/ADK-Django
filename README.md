# `ADK Django`

```bash
python3 -m venv .venv
source .venv/bin/activate       # ubuntu
.\.venv\Scripts\activate        # powershell

pip install -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate

python3 manage.py collectstatic
python3 manage.py createsuperuser
daphne myadk.asgi:application -b 0.0.0.0 -p 8000
```

>## *Surface Web*
>![surfaceweb](https://github.com/user-attachments/assets/63950d30-f535-4cfb-943d-aa2617fc45bb)
>
>## *Dark Web*
>![darkweb](https://github.com/user-attachments/assets/21706950-2a4d-4e50-8ecc-aefdc0ea9a30)
>
>## *Flutter App*
>![20251005_181354-COLLAGE](https://github.com/user-attachments/assets/c97f1d2c-dfd7-4320-bc57-2c5ef2f5585c)

## `To do List`:

1.  **Dynamic UI & BYOK Data Model (Django):** Configure a single **`TenantCompany` model** to store all dynamic branding (logo URL, colors) and per-tenant settings (LLM choice, System Prompt). Authenticated **Django views** must fetch and pass this model's data via the context dictionary for all UI rendering and backend API calls (Bring Your Own Key - BYOK).

2.  **Voice AI Orchestration (Flask/Webhooks):** Implement a separate, lightweight **Flask application** exposed via a public URL (e.g., Twilio webhook). This app must contain two endpoints, `start_call` and `process_prompt`, that use **TwiML/NCL** to manage the call flow, perform **Speech-to-Text (STT)**, call the Groq/Gemini API (using the key from the Django DB), and perform **Text-to-Speech (TTS)**.

3.  **Cross-Platform Data Integration:** Ensure the Flask (call) logic accesses the same **Django database** (e.g., using PostgreSQL/MySQL container setup instead of SQLite) to retrieve the user's specific **API key** and **LLM model name** for reply generation, unifying the settings across both the chat and call interfaces.
