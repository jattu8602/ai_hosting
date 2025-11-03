#!/bin/bash

# Deployment script for LLM Chat System
# This script helps deploy to the VM

set -e

VM_IP="210.79.129.25"
APP_DIR="/opt/llm-chat"

echo "=========================================="
echo "LLM Chat System - Deployment Script"
echo "=========================================="
echo ""
echo "This script will help you deploy to: $VM_IP"
echo ""

# Ask for deployment method
echo "Choose deployment method:"
echo "1) Docker (Recommended)"
echo "2) PM2"
read -p "Enter choice [1 or 2]: " choice

echo ""
echo "Step 1: Copying files to VM..."
echo "Please provide SSH user (e.g., ubuntu, root):"
read -p "SSH User: " ssh_user

echo "Copying files..."
rsync -avz --exclude 'data/' --exclude '.git' \
    ./ ${ssh_user}@${VM_IP}:${APP_DIR}/

echo ""
echo "Step 2: Generating SSL certificate on VM..."
ssh ${ssh_user}@${VM_IP} "cd ${APP_DIR} && chmod +x ssl/generate-cert.sh && ./ssl/generate-cert.sh"

if [ "$choice" = "1" ]; then
    echo ""
    echo "Step 3: Building and starting Docker container..."
    ssh ${ssh_user}@${VM_IP} "cd ${APP_DIR} && docker-compose build && docker-compose up -d"
    echo ""
    echo "Deployment complete with Docker!"
    echo "Check logs: ssh ${ssh_user}@${VM_IP} 'cd ${APP_DIR} && docker-compose logs -f'"
elif [ "$choice" = "2" ]; then
    echo ""
    echo "Step 3: Setting up PM2..."
    ssh ${ssh_user}@${VM_IP} "cd ${APP_DIR} && pip3 install -r requirements.txt && pm2 start pm2.config.js && pm2 save && pm2 startup"
    echo ""
    echo "Deployment complete with PM2!"
    echo "Check logs: ssh ${ssh_user}@${VM_IP} 'pm2 logs llm-chat-api'"
fi

echo ""
echo "API will be available at:"
echo "  HTTP:  http://${VM_IP}:8000"
echo "  HTTPS: https://${VM_IP}:8000 (use -k flag with curl)"
echo ""
echo "Test health: curl http://${VM_IP}:8000/health"

