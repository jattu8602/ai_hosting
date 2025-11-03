# LLM Chat System with Learning Capabilities

A fast, lightweight chat system powered by GPT-2 with RAG (Retrieval Augmented Generation) that learns from user teachings and stores knowledge for future use.

## Architecture

- **Model**: GPT-2 (124M parameters, ~500MB, optimized for speed)
- **Learning**: ChromaDB vector database for knowledge storage and retrieval
- **API**: FastAPI with HTTPS support
- **Process Management**: PM2
- **Containerization**: Docker (optional)

## Features

- 💬 Fast chat with GPT-2 model (5-17 second responses)
- 🧠 Learn from user teachings (e.g., chess rules)
- 🔍 Retrieve learned knowledge during conversations
- 🚀 Async background learning (no response delay)
- 🐳 Docker containerization (optional)
- 🔒 HTTPS support (self-signed certificate)
- 📊 PM2 process management

## 📚 Documentation

- **[Complete Deployment Guide](./DEPLOYMENT_GUIDE.md)** - Full documentation for hosting with API endpoints
- **[Easy Deployment Options](./EASY_DEPLOY.md)** - Quick reference for fastest deployment methods
- **[Platform-Specific Setup](./PLATFORM_SETUP.md)** - Ready-to-use configs for each platform

## Prerequisites

- Ubuntu VM with 2 vCPU, 4GB RAM
- Docker installed
- Python 3.11+
- Node.js and npm (for PM2)

## Quick Setup

### 1. Connect to VM and Run Setup

```bash
ssh user@210.79.129.25
sudo bash setup.sh
```

### 2. Copy Files to VM

Copy all files to `/opt/llm-chat/` on the VM:

```bash
scp -r * user@210.79.129.25:/opt/llm-chat/
```

### 3. Generate SSL Certificate

```bash
cd /opt/llm-chat
chmod +x ssl/generate-cert.sh
./ssl/generate-cert.sh
```

### 4. Deploy with Docker

```bash
cd /opt/llm-chat
docker-compose build
docker-compose up -d
```

### 5. OR Deploy with PM2

```bash
cd /opt/llm-chat
pip install -r requirements.txt
pm2 start pm2.config.js
pm2 save
pm2 startup  # Set up auto-start on boot
```

## API Endpoints

### Health Check
```bash
GET /health
```

### Chat
```bash
POST /chat
Content-Type: application/json

{
  "message": "How do I play chess?",
  "conversation_id": "optional-id"
}
```

### Teach (Store Knowledge)
```bash
POST /teach
Content-Type: application/json

{
  "knowledge": "In chess, the king can move one square in any direction. The queen can move any number of squares in any direction.",
  "topic": "chess"
}
```

### Get Knowledge
```bash
GET /knowledge?topic=chess
```

## Example Usage

1. **Teach the model about chess:**
```bash
curl -X POST https://210.79.129.25:8000/teach \
  -H "Content-Type: application/json" \
  -d '{
    "knowledge": "In chess, the king moves one square in any direction. The queen moves any number of squares horizontally, vertically, or diagonally.",
    "topic": "chess"
  }'
```

2. **Chat and ask about chess:**
```bash
curl -X POST https://210.79.129.25:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How does the king move in chess?"
  }' \
  -k  # -k flag for self-signed certificate
```

The model will retrieve the learned knowledge and use it in the response!

## How Learning Works

1. User teaches knowledge via `/teach` endpoint
2. Knowledge is validated and stored in ChromaDB with embeddings
3. When user asks a question via `/chat`:
   - System searches for relevant knowledge using embeddings
   - Retrieves top matching knowledge items
   - Includes them as context when generating response
4. Model uses both its training and learned knowledge to answer

## File Structure

```
/opt/llm-chat/
├── app/
│   ├── main.py          # FastAPI application
│   ├── model.py         # Phi-2 model loading
│   ├── embeddings.py    # Embedding model
│   ├── knowledge.py     # ChromaDB knowledge storage
│   ├── chat.py          # Chat handler
│   └── config.py        # Configuration
├── data/                # Persistent data
│   ├── models/          # Model cache
│   └── chromadb/        # Vector database
├── ssl/                 # SSL certificates
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pm2.config.js
└── setup.sh
```

## Resource Management

- **Model**: ~500MB (GPT-2, optimized for speed)
- **Embeddings**: ~100MB (sentence-transformers)
- **ChromaDB**: In-memory with persistence
- **Total**: Optimized for 4GB RAM VM
- **Response Time**: 5-17 seconds (CPU-only, optimized)

## Deployment Options

This project supports multiple deployment methods:

1. **Self-Hosted VM** (Current method) - Full control, manual setup
2. **Hugging Face Spaces** - Easiest, free tier available
3. **Replicate** - One-click deployment, pay-per-use
4. **RunPod** - Budget GPU hosting ($0.20/hr)
5. **Railway/Render** - GitHub auto-deploy

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for detailed instructions on each platform.

## Troubleshooting

### Model Loading Issues
- Ensure sufficient disk space (~10GB for model download)
- Check RAM usage: `free -h`
- Monitor with: `docker stats` or `pm2 monit`

### SSL Certificate Warnings
- Self-signed certificates will show browser warnings
- Use `-k` flag with curl for testing
- Click "Advanced" -> "Proceed" in browser

### Port Already in Use
```bash
# Check what's using the port
sudo lsof -i :8000
# Or kill Docker container
docker-compose down
```

## Monitoring

### Docker
```bash
docker-compose logs -f
docker stats
```

### PM2
```bash
pm2 status
pm2 logs
pm2 monit
```

## License

This project is for educational purposes.

# ai_hosting
