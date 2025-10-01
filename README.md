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

![image](https://github.com/user-attachments/assets/21c51fc0-3a7c-49be-8290-13a2b37149ca)
