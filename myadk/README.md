# ADK Django Chat Application Deployment

This repository contains the source code for the **ADK Django Chat Application**, containerized using Docker for consistent, portable deployment across any environment (local, staging, or production server).

## 🚀 Quick Start (Pull & Run)

If you have Docker installed, you can launch the application instantly using the image available on Docker Hub.

### 1\. Pull the Image

Download the latest version of the application image to your machine:

```bash
docker pull imvickykumar999/myadk-django:latest
```

### 2\. Run the Container

Use the `docker run` command to create and start a new container. We recommend using a **volume** to ensure your chat history and user data (stored in `db.sqlite3`) are saved persistently on your host machine.

```bash
# ⚠️ IMPORTANT: Replace /path/to/local/data with an actual empty folder path on your machine.
docker run -d \
  -p 8000:8000 \
  -v /path/to/local/data:/usr/src/app \
  --name myadk-web-production \
  imvickykumar999/myadk-django:latest
```

| Parameter | Function |
| :--- | :--- |
| `-d` | Runs the container in **detached mode** (background). |
| `-p 8000:8000` | **Maps Host Port 8000** to the Container's internal port 8000. |
| `-v ...` | Creates a **persistent volume** for the database and static files. |
| `--name ...` | Assigns a memorable container name. |

### 3\. Access the Application

Open your browser and navigate to:

```
http://localhost:8000
```

-----

## ⚙️ Container Management (Start, Stop, Status)

Once the container is created with `--name myadk-web-production`, you can control it using simple commands:

### Check Status

View the status and logs to ensure the server started correctly:

| Action | Command |
| :--- | :--- |
| **Check if running** | `docker ps` |
| **View startup logs** | `docker logs myadk-web-production` |

### Stop and Start

| Action | Command | Effect |
| :--- | :--- | :--- |
| **Stop** (`DOWN`) | `docker stop myadk-web-production` | Gracefully stops the application, but the container instance is preserved (`Exited` state). |
| **Start** (`UP`) | `docker start myadk-web-production` | Starts the existing, stopped container instance again. |

### Remove/Clean Up

To completely remove the container instance (freeing up the port and name):

```bash
docker rm myadk-web-production
```

-----

## 🛠️ Developer Workflow (Build, Tag, Push)

This section documents the process used to update the image when the local code (e.g., HTML files) changes.

### 1\. Build the New Image

After making local changes (e.g., in HTML, Python, or `Dockerfile`), rebuild the image using the same tag. Docker's cache makes this process fast by only rebuilding the layers that changed.

```bash
docker build . -t imvickykumar999/myadk-django:latest
```

### 2\. Login to Docker Hub

Ensure you are authenticated to push to your namespace:

```bash
docker login
# Enter username: imvickykumar999 and password when prompted
```

### 3\. Push the Updated Image

Upload the newly built image (with the code changes) to Docker Hub. Docker will only push the new layers.

```bash
docker push imvickykumar999/myadk-django:latest
```

### 4\. Deploy the Update

On the target server, you deploy the update by stopping the old container, pulling the new image, and starting a fresh container instance:

```bash
# 1. Stop and remove the old container
docker stop myadk-web-production
docker rm myadk-web-production

# 2. Pull the updated image
docker pull imvickykumar999/myadk-django:latest

# 3. Start a new container instance with the persistent volume
docker run -d \
  -p 8000:8000 \
  -v /path/to/local/data:/usr/src/app \
  --name myadk-web-production \
  imvickykumar999/myadk-django:latest
```
