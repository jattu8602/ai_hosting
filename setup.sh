#!/bin/bash

# Setup script for LLM Chat System on Ubuntu VM
# This script installs prerequisites and sets up the system

set -e

echo "=========================================="
echo "LLM Chat System - Setup Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root or with sudo${NC}"
    exit 1
fi

# Update system
echo -e "${YELLOW}[1/6] Updating system packages...${NC}"
apt-get update

# Install prerequisites
echo -e "${YELLOW}[2/6] Installing prerequisites...${NC}"
apt-get install -y \
    docker.io \
    docker-compose \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    wget \
    git \
    build-essential \
    openssl \
    npm

# Start and enable Docker
echo -e "${YELLOW}[3/6] Starting Docker service...${NC}"
systemctl start docker
systemctl enable docker

# Install PM2 globally
echo -e "${YELLOW}[4/6] Installing PM2...${NC}"
npm install -g pm2

# Create application directory
APP_DIR="/opt/llm-chat"
echo -e "${YELLOW}[5/6] Creating application directory: $APP_DIR${NC}"
mkdir -p "$APP_DIR"
mkdir -p "$APP_DIR/data/models"
mkdir -p "$APP_DIR/data/chromadb"
mkdir -p "$APP_DIR/logs"
mkdir -p "$APP_DIR/ssl"

# Set permissions
chmod -R 755 "$APP_DIR"

# Generate SSL certificate
echo -e "${YELLOW}[6/6] Generating SSL certificate...${NC}"
cd "$APP_DIR"
if [ -f "ssl/generate-cert.sh" ]; then
    chmod +x ssl/generate-cert.sh
    ./ssl/generate-cert.sh
else
    echo -e "${RED}SSL generation script not found. Please generate certificate manually.${NC}"
fi

echo ""
echo -e "${GREEN}=========================================="
echo "Setup completed successfully!"
echo "==========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Copy application files to $APP_DIR"
echo "2. Build Docker image: cd $APP_DIR && docker-compose build"
echo "3. Start service: docker-compose up -d"
echo "   OR use PM2: pm2 start pm2.config.js"
echo ""
echo "For HTTPS, ensure SSL certificates are in $APP_DIR/ssl/"

