# ADK Django

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py collectstatic
python3 manage.py createsuperuser
daphne myadk.asgi:application -b 0.0.0.0 -p 8000
```

<img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/f0ab7f7d-29dc-4ba3-8d7e-3118b124184d" />

<img width="1320" height="700" alt="image" src="https://github.com/user-attachments/assets/a33820b9-f523-4c93-957e-15a8f8c3fa68" />
