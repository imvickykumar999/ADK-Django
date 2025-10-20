#!/bin/bash
#
# Script: undeploy.sh
# Purpose: Cleans up all Kubernetes and Minikube resources created by deploy.sh.
#          This stops the port forwarding, deletes the deployment/service,
#          and finally stops the Minikube cluster.
#
# USAGE:
# 1. Save the file: chmod +x undeploy.sh
# 2. Run: ./undeploy.sh

# --- Configuration Variables (Must match deploy.sh) ---
K8S_YAML_FILE="k8s_deployment.yaml"
APP_SERVICE="myadk-web-service"
LOCAL_PORT=8000 # The port to check for the port-forward process

echo "--- Starting Undeployment and Cleanup ---"

# --- 1. Stop Port Forwarding Process ---
echo "1. Attempting to stop background port-forwarding on port ${LOCAL_PORT}..."

# Find the PID of the process forwarding from the specific local port
# Uses 'lsof' to list files open by processes, specifically looking for TCP connections
# on LOCAL_PORT, filters for 'LISTEN', and extracts the PID.
FORWARD_PID=$(sudo lsof -t -i :${LOCAL_PORT} -sTCP:LISTEN 2>/dev/null)

if [ -n "$FORWARD_PID" ]; then
    echo "   Found port-forward process (PID: ${FORWARD_PID}). Killing..."
    # Attempt to kill the process
    kill "$FORWARD_PID"
    if [ $? -eq 0 ]; then
        echo "   Port-forwarding process stopped successfully."
    else
        echo "   Warning: Failed to kill process ${FORWARD_PID}. You may need to kill it manually."
    fi
else
    echo "   No active process found listening on port ${LOCAL_PORT}."
fi


# --- 2. Delete Kubernetes Resources ---
echo "2. Deleting Kubernetes Deployment and Service from Minikube..."

if [ -f "${K8S_YAML_FILE}" ]; then
    kubectl delete -f "${K8S_YAML_FILE}" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "   Resources defined in ${K8S_YAML_FILE} deleted successfully."
    else
        # This might happen if the resources were already deleted or kubectl is not working.
        echo "   Warning: Could not delete resources via kubectl. They might already be removed."
    fi
else
    echo "   Warning: Kubernetes manifest file (${K8S_YAML_FILE}) not found. Cannot explicitly delete resources."
fi


# --- 3. Stop and Delete Minikube Cluster ---
echo "3. Stopping and deleting Minikube cluster..."
# Stop the Minikube virtual machine
minikube stop 2>/dev/null
echo "   Minikube cluster stopped."
# Delete the cluster completely
minikube delete 2>/dev/null
echo "   Minikube cluster deleted."


# --- 4. Cleanup Manifest File ---
echo "4. Removing temporary Kubernetes manifest file (${K8S_YAML_FILE})."
rm -f "${K8S_YAML_FILE}"

echo ""
echo "=========================================================="
echo "✅ UNDEPLOYMENT COMPLETE"
echo "All resources and processes have been cleaned up."
echo "=========================================================="
