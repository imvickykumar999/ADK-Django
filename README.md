# ADK Django

```bash
git clone https://github.com/imvickykumar999/ADK-Django.git
cd ADK-Django/myadk
python -m venv .venv

source .venv/bin/activate       # ubuntu/macOS
.\.venv\Scripts\activate        # powershell

pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate

python manage.py collectstatic
python manage.py createsuperuser
python manage.py runserver 8000
```

![editable form](https://github.com/user-attachments/assets/fccd2e28-b47a-4578-8f52-5dd1ceb9de98)

>## *Surface Web*
>![surfaceweb](https://github.com/user-attachments/assets/63950d30-f535-4cfb-943d-aa2617fc45bb)
>
>## *Dark Web*
>![darkweb](https://github.com/user-attachments/assets/21706950-2a4d-4e50-8ecc-aefdc0ea9a30)
>
>## *Flutter App*
>![20251005_181354-COLLAGE](https://github.com/user-attachments/assets/c97f1d2c-dfd7-4320-bc57-2c5ef2f5585c)

# `Custom Branding`

![mcd](https://github.com/user-attachments/assets/e2616f54-0696-49db-aeba-84dd740e9b39)
![dominos](https://github.com/user-attachments/assets/0086a897-6b65-465a-a146-fe02cdce6dc9)
![minecraft](https://github.com/user-attachments/assets/98298421-363b-43f4-864b-e9d6c4b5608c)
![admin](https://github.com/user-attachments/assets/725f8037-ea33-4e16-b6b2-2d77fa9a74f0)

## How to Pull and Run the Application

Any machine with the Docker Engine installed (including a cloud server or a local computer) can start your application using the following two commands:

### 1\. Pull the Image

This command downloads the latest version of your application from your Docker Hub repository.

```bash
docker pull imvickykumar999/myadk-django:latest
```

### 2\. Run the Container

This command starts the application, sets a name, and maps the port for access.

```bash
docker run -d \
  -p 8000:8000 \
  --name myadk-web-production \
  imvickykumar999/myadk-django:latest
```

| Parameter | Function |
| :--- | :--- |
| **`-d`** | Runs the container in **detached mode** (in the background). |
| **`-p 8000:8000`** | **Maps Host Port 8000** to the Container's internal port 8000. |
| **`--name ...`** | Assigns the container an **easy-to-reference name**. |

-----

| Action | Command | Purpose |
| :--- | :--- | :--- |
| **Download Image** | `docker pull imvickykumar999/myadk-django:latest` | Downloads the application image from Docker Hub to your local machine. |
| **Initial Run** | `docker run -d -p 8000:8000 --name myadk-web-production imvickykumar999/myadk-django:latest` | Creates and starts a **new** container from the image in detached mode, naming it `myadk-web-production` and mapping the ports. |
| **Stop Container** | `docker stop myadk-web-production` | **Gracefully stops** the running container. |
| **Start Container** | `docker start myadk-web-production` | **Restarts** the previously stopped container. |
| **View Running** | `docker ps` | Lists all currently **running** containers. |
| **View All** | `docker ps -a` | Lists **all** containers (running, stopped, etc.). |
| **Remove Container** | `docker rm myadk-web-production` | **Deletes** the container from your system (must be stopped first). |
| **Force Stop** | `docker kill myadk-web-production` | Immediately **forces** the container to stop (less graceful than `docker stop`). |
