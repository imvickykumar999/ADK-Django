# ADK Django Chat Application Deployment

### How to Run This Script

1.  **Save the file:** Save the content above as `deploy.sh` in your project root.
2.  **Make it executable:** Run `chmod +x deploy.sh` in your terminal.
3.  **Execute:** Run `./deploy.sh`
4.  The script will print the process ID (`FORWARD_PID`) and instructions for accessing and cleaning up the service.

---

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

-----

## Kubernetes Deployment & Local Access Guide

This guide details the steps required to deploy the `myadk-django` Docker image onto a local Kubernetes cluster (Minikube) within your Codespace environment and access it locally via port 8000.

### Prerequisites

  * **Docker** is installed (available by default in Codespaces).
  * The Kubernetes manifest file (`k8s_deployment.yaml`) must be present in the root directory.

-----

### 1\. Minikube Setup & Cluster Start

First, install and start the local Kubernetes cluster:

**A. Install Minikube**

Download the binary and install it to make the `minikube` command available:

```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

**B. Start the Cluster**

Start Minikube using the Docker driver. This configures the `kubectl` tool automatically.

```bash
minikube start --driver=docker
```

**C. Verify Connection**

Ensure the cluster is running:

```bash
kubectl get nodes
```

*(Expected Output: `minikube` with `STATUS: Ready`)*

-----

### 2\. Secure Deployment

These steps deploy your application and securely inject your API key.

**A. Securely Inject the API Key (Secret)**

Creates a Kubernetes Secret to pass your API key to the container's `YOUR_API_KEY` environment variable.

```bash
kubectl create secret generic myadk-secrets --from-literal=api-key='YOUR_ACTUAL_API_KEY'
```

**B. Apply the Kubernetes Manifest**

Creates the Deployment (3 running containers) and the LoadBalancer Service defined in your YAML.

```bash
kubectl apply -f k8s_deployment.yaml
```

**C. Monitor Deployment Status**

Wait for the application Pods to be fully up and running:

```bash
kubectl rollout status deployment/myadk-web-deployment
```

-----

### 3\. Local Access and Debugging

Since your Django application expects traffic on port **8000** and we cannot use privileged ports, we forward the service to port 8000.

**A. Forward Traffic to Port 8000**

Run this command in a **new, separate terminal tab** and **leave it running**. This resolves the **permission denied** and **CSRF verification** issues by routing the traffic through the expected port.

```bash
kubectl port-forward service/myadk-web-service 8000:8000
```

**B. Access the Application**

Access the application via your Codespace's **"PORTS"** tab on port **8000**, or navigate directly to:

`http://localhost:8000`

-----

### Cleanup (Stopping the Cluster)

Use these commands to stop and remove all resources when you are finished testing:

| Action | Command | Purpose |
| :--- | :--- | :--- |
| **Stop Forwarding** | (In the terminal running `kubectl port-forward`): **Press `Ctrl+C`** | Stops the local access tunnel. |
| **Delete App** | `kubectl delete -f k8s_deployment.yaml` | Deletes the Deployment and Service. |
| **Stop Minikube** | `minikube stop` | Shuts down the local Kubernetes virtual machine. |
| **Delete Cluster** | `minikube delete` | Completely removes the Minikube cluster and configuration. |
