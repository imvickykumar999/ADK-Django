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

<img width="1535" height="882" alt="image" src="https://github.com/user-attachments/assets/630c3374-c66e-41c9-8417-29d61fac022c" />
