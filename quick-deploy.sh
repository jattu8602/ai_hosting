#!/bin/bash
# Quick deployment - modify SSH_USER before running

SSH_USER="ubuntu"  # <-- CHANGE THIS to your SSH username
VM_IP="210.79.129.25"
APP_DIR="/opt/llm-chat"
LOCAL_DIR="/Users/jattu/Desktop/ai"

echo "Deploying to $SSH_USER@$VM_IP..."

# Step 1: Copy setup script and run it
echo "Step 1: Setting up VM..."
scp ${LOCAL_DIR}/setup.sh ${SSH_USER}@${VM_IP}:/tmp/
ssh ${SSH_USER}@${VM_IP} "sudo bash /tmp/setup.sh"

# Step 2: Copy all files
echo "Step 2: Copying files..."
ssh ${SSH_USER}@${VM_IP} "sudo mkdir -p ${APP_DIR} && sudo chown -R ${SSH_USER}:${SSH_USER} ${APP_DIR}"
rsync -avz --exclude 'data/' --exclude '.git' ${LOCAL_DIR}/ ${SSH_USER}@${VM_IP}:${APP_DIR}/
ssh ${SSH_USER}@${VM_IP} "cd ${APP_DIR} && chmod +x *.sh ssl/*.sh"

# Step 3: Generate SSL
echo "Step 3: Generating SSL certificate..."
ssh ${SSH_USER}@${VM_IP} "cd ${APP_DIR} && ./ssl/generate-cert.sh"

# Step 4: Deploy with Docker (default)
echo "Step 4: Building and starting Docker container..."
ssh ${SSH_USER}@${VM_IP} "cd ${APP_DIR} && docker-compose build && docker-compose up -d"

echo "Done! API will be available at http://${VM_IP}:8000"
echo "Test: curl http://${VM_IP}:8000/health"

