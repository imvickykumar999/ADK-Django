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

![surfaceweb](https://github.com/user-attachments/assets/63950d30-f535-4cfb-943d-aa2617fc45bb)
![darkweb](https://github.com/user-attachments/assets/21706950-2a4d-4e50-8ecc-aefdc0ea9a30)

