# Quick Start Guide

## Step 1: Connect to VM

```bash
ssh user@210.79.129.25
```

## Step 2: Run Setup Script

```bash
sudo bash setup.sh
```

This installs Docker, Python, PM2, and other prerequisites.

## Step 3: Copy Files to VM

From your local machine:

```bash
cd /Users/jattu/Desktop/ai
scp -r * user@210.79.129.25:/opt/llm-chat/
```

Or use the deploy script:

```bash
chmod +x deploy.sh
./deploy.sh
```

## Step 4: Generate SSL Certificate

On the VM:

```bash
cd /opt/llm-chat
./ssl/generate-cert.sh
```

## Step 5: Deploy (Choose One)

### Option A: Docker (Recommended)

```bash
cd /opt/llm-chat
docker-compose build
docker-compose up -d
docker-compose logs -f  # View logs
```

### Option B: PM2

```bash
cd /opt/llm-chat
pip3 install -r requirements.txt
pm2 start pm2.config.js
pm2 save
pm2 startup  # Set auto-start on boot
pm2 logs llm-chat-api  # View logs
```

## Step 6: Test the API

```bash
# Health check
curl http://210.79.129.25:8000/health

# Teach about chess
curl -X POST http://210.79.129.25:8000/teach \
  -H "Content-Type: application/json" \
  -d '{
    "knowledge": "In chess, the king moves one square in any direction.",
    "topic": "chess"
  }'

# Chat
curl -X POST http://210.79.129.25:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How does the king move in chess?"
  }'
```

## Troubleshooting

- **Port in use**: `sudo lsof -i :8000` then kill the process
- **Docker issues**: `docker-compose down` then `docker-compose up -d`
- **PM2 issues**: `pm2 restart llm-chat-api` or `pm2 delete llm-chat-api`
- **SSL warnings**: Use `-k` flag with curl for self-signed certificates

