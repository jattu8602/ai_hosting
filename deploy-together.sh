#!/bin/bash

# Interactive deployment script - guides you through each step

set -e

VM_IP="210.79.129.25"
APP_DIR="/opt/llm-chat"
LOCAL_DIR="/Users/jattu/Desktop/ai"

echo "=========================================="
echo "LLM Chat System - Step-by-Step Deployment"
echo "=========================================="
echo ""
echo "VM IP: $VM_IP"
echo "App Directory: $APP_DIR"
echo ""

# Step 1: Get SSH credentials
echo "Step 1: SSH Credentials"
echo "----------------------"
read -p "Enter SSH username (e.g., ubuntu, root): " SSH_USER

# Test connection
echo ""
echo "Testing SSH connection..."
if ssh -o ConnectTimeout=5 -o BatchMode=yes ${SSH_USER}@${VM_IP} exit 2>/dev/null; then
    echo "✓ SSH connection successful!"
else
    echo "⚠ SSH connection test failed or requires password/key."
    echo "Please ensure you can SSH to the VM manually first."
    read -p "Press Enter to continue anyway, or Ctrl+C to exit..."
fi

# Step 2: Run setup script on VM
echo ""
echo "Step 2: Running Setup Script on VM"
echo "-----------------------------------"
echo "This will install Docker, Python, PM2, and other prerequisites..."
read -p "Continue? (y/n): " continue_setup

if [ "$continue_setup" = "y" ]; then
    echo "Copying setup script to VM..."
    scp ${LOCAL_DIR}/setup.sh ${SSH_USER}@${VM_IP}:/tmp/setup.sh

    echo "Running setup script (requires sudo)..."
    ssh ${SSH_USER}@${VM_IP} "sudo bash /tmp/setup.sh"
    echo "✓ Setup complete!"
else
    echo "Skipping setup..."
fi

# Step 3: Copy files to VM
echo ""
echo "Step 3: Copying Application Files to VM"
echo "----------------------------------------"
read -p "Copy files to VM? (y/n): " copy_files

if [ "$copy_files" = "y" ]; then
    echo "Creating directory on VM..."
    ssh ${SSH_USER}@${VM_IP} "sudo mkdir -p ${APP_DIR} && sudo chown -R ${SSH_USER}:${SSH_USER} ${APP_DIR}"

    echo "Copying files (this may take a moment)..."
    rsync -avz --progress \
        --exclude 'data/' \
        --exclude '.git' \
        --exclude '__pycache__' \
        --exclude '*.pyc' \
        ${LOCAL_DIR}/ ${SSH_USER}@${VM_IP}:${APP_DIR}/

    echo "Setting permissions..."
    ssh ${SSH_USER}@${VM_IP} "cd ${APP_DIR} && chmod +x *.sh ssl/*.sh"

    echo "✓ Files copied successfully!"
else
    echo "Skipping file copy..."
fi

# Step 4: Generate SSL certificate
echo ""
echo "Step 4: Generating SSL Certificate"
echo "-----------------------------------"
read -p "Generate SSL certificate? (y/n): " gen_ssl

if [ "$gen_ssl" = "y" ]; then
    echo "Generating SSL certificate on VM..."
    ssh ${SSH_USER}@${VM_IP} "cd ${APP_DIR} && ./ssl/generate-cert.sh"
    echo "✓ SSL certificate generated!"
else
    echo "Skipping SSL generation..."
fi

# Step 5: Choose deployment method
echo ""
echo "Step 5: Deploy Application"
echo "---------------------------"
echo "Choose deployment method:"
echo "1) Docker (Recommended - easier to manage)"
echo "2) PM2 (Direct process management)"
read -p "Enter choice [1 or 2]: " deploy_choice

if [ "$deploy_choice" = "1" ]; then
    echo ""
    echo "Deploying with Docker..."
    ssh ${SSH_USER}@${VM_IP} "cd ${APP_DIR} && docker-compose build"
    echo ""
    read -p "Docker build complete. Start container? (y/n): " start_docker
    if [ "$start_docker" = "y" ]; then
        ssh ${SSH_USER}@${VM_IP} "cd ${APP_DIR} && docker-compose up -d"
        echo "✓ Docker container started!"
        echo ""
        echo "View logs with: ssh ${SSH_USER}@${VM_IP} 'cd ${APP_DIR} && docker-compose logs -f'"
    fi
elif [ "$deploy_choice" = "2" ]; then
    echo ""
    echo "Deploying with PM2..."
    ssh ${SSH_USER}@${VM_IP} "cd ${APP_DIR} && pip3 install --user -r requirements.txt"
    echo ""
    read -p "Dependencies installed. Start with PM2? (y/n): " start_pm2
    if [ "$start_pm2" = "y" ]; then
        ssh ${SSH_USER}@${VM_IP} "cd ${APP_DIR} && pm2 start pm2.config.js && pm2 save"
        echo "✓ PM2 started!"
        echo ""
        echo "View logs with: ssh ${SSH_USER}@${VM_IP} 'pm2 logs llm-chat-api'"
    fi
fi

# Step 6: Test the API
echo ""
echo "Step 6: Testing the API"
echo "-----------------------"
read -p "Wait a moment for the service to start, then test? (y/n): " test_api

if [ "$test_api" = "y" ]; then
    echo "Waiting 10 seconds for service to start..."
    sleep 10

    echo ""
    echo "Testing /health endpoint..."
    curl -s http://${VM_IP}:8000/health | python3 -m json.tool || echo "Service not ready yet. Wait a bit longer and try: curl http://${VM_IP}:8000/health"

    echo ""
    echo "API should be available at:"
    echo "  HTTP:  http://${VM_IP}:8000"
    echo "  HTTPS: https://${VM_IP}:8000 (use -k flag with curl)"
fi

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Teach the model: curl -X POST http://${VM_IP}:8000/teach -H 'Content-Type: application/json' -d '{\"knowledge\":\"...\",\"topic\":\"chess\"}'"
echo "2. Chat: curl -X POST http://${VM_IP}:8000/chat -H 'Content-Type: application/json' -d '{\"message\":\"...\"}'"
echo "3. Check logs: ssh ${SSH_USER}@${VM_IP} and view Docker/PM2 logs"

