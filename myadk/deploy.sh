#!/bin/bash
#
# Script: deploy.sh
# Purpose: Installs Minikube, deploys the myadk-web application, and forwards traffic.
#          NOTE: All API Key/Secret functionality has been removed as requested.
#
# USAGE:
# 1. Save the file: chmod +x deploy.sh
# 2. Run: ./deploy.sh
# 3. Stop (optional): kill $FORWARD_PID (where $FORWARD_PID is printed by the script)
#                     minikube delete

# --- Configuration Variables ---
K8S_YAML_FILE="k8s_deployment.yaml"
APP_SERVICE="myadk-web-service"
LOCAL_PORT=8000
K8S_PORT=8000

# --- Function to Check for Required Commands ---
check_command() {
    command -v "$1" >/dev/null 2>&1
}

# --- 1. Installation and Setup Check ---

echo "--- 1. Checking Environment and Installing Minikube ---"

# Check and install Minikube if not found
if ! check_command minikube; then
    echo "Minikube not found. Installing..."
    curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
    sudo install minikube-linux-amd64 /usr/local/bin/minikube
    rm minikube-linux-amd64
    echo "Minikube installed."
fi

# Check for kubectl
if ! check_command kubectl; then
    echo "kubectl not found. Please ensure it is installed and in your PATH."
    exit 1
fi


# --- 2. Write Kubernetes YAML File ---
echo "--- 2. Creating Kubernetes Manifest: ${K8S_YAML_FILE} ---"

# Write the YAML content (without API Key references)
cat <<EOF > ${K8S_YAML_FILE}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myadk-web-deployment
  labels:
    app: myadk-web
spec:
  # Instruct Kubernetes to always run 3 copies of your application for high availability
  replicas: 3
  selector:
    matchLabels:
      app: myadk-web
  template:
    metadata:
      labels:
        app: myadk-web
    spec:
      containers:
      - name: myadk-django-container
        # This is where Kubernetes "pulls" your image from Docker Hub
        image: imvickykumar999/myadk-django:latest
        ports:
        - containerPort: 8000 # This must match the port exposed in your Dockerfile (8000)
        
        # --- Environment Variables ---
        env:
        # Django needs to know the external host and internal cluster IP it can trust.
        - name: DJANGO_ALLOWED_HOSTS
          value: "localhost,127.0.0.1,10.111.97.107" # Added cluster IP as allowed host
        - name: CSRF_TRUSTED_ORIGINS # Django must trust the origin URL accessed by the user
          value: "http://localhost:8000" # Expects traffic on port 8000
---
apiVersion: v1
kind: Service
metadata:
  name: myadk-web-service
spec:
  # Use LoadBalancer type to expose the app externally
  type: LoadBalancer
  selector:
    app: myadk-web # Matches the label in the Deployment above to route traffic
  ports:
    - protocol: TCP
      port: 8000           # The port the Load Balancer listens on (external access)
      targetPort: 8000     # The port the container is listening on (internal to the pod)
EOF


# --- 3. Start Minikube Cluster ---
echo "--- 3. Starting Minikube Cluster with Docker Driver ---"
minikube start --driver=docker

# Wait for Minikube to be fully ready
kubectl wait --for=condition=ready node minikube --timeout=300s
echo "Cluster is ready."


# --- 4. Create Kubernetes Secret (Skipped) ---
echo "--- 4. Secret Creation Skipped (No API Key Required) ---"


# --- 5. Apply the Deployment ---
echo "--- 5. Deploying Application Resources ---"
kubectl apply -f ${K8S_YAML_FILE}

# Wait for the deployment to roll out
echo "Waiting for deployment to roll out..."
kubectl rollout status deployment/myadk-web-deployment --timeout=300s

if [ $? -eq 0 ]; then
    echo "Deployment successful."
else
    echo "Deployment failed or timed out. Check 'kubectl get pods'."
    exit 1
fi


# --- 6. Start Port Forwarding (Background) ---
echo "--- 6. Starting Port Forwarding (Background) ---"
# Start forwarding in the background to free up the terminal
kubectl port-forward service/${APP_SERVICE} ${LOCAL_PORT}:${K8S_PORT} > /dev/null 2>&1 &

# Store the Process ID for cleanup
FORWARD_PID=$!

echo ""
echo "=========================================================="
echo "✅ DEPLOYMENT COMPLETE & SERVICE IS RUNNING"
echo "=========================================================="
echo "Your application is accessible at:"
echo "   http://localhost:${LOCAL_PORT}"
echo ""
echo "To stop the service and cleanup:"
echo "1. Stop the Port Forwarding process: kill ${FORWARD_PID}"
echo "2. Stop Minikube: minikube stop"
echo "3. Delete all Kubernetes resources: kubectl delete -f ${K8S_YAML_FILE}"
echo "4. Delete Minikube cluster: minikube delete"
echo "=========================================================="

# Exit with the PID in the terminal prompt for easy reference
exit 0
