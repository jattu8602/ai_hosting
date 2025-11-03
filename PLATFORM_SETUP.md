# Platform-Specific Setup Files

This document contains ready-to-use configurations for each deployment platform.

---

## 1. Hugging Face Spaces

### File Structure for HF Spaces:
```
your-space/
├── app.py              # Main application
├── requirements.txt    # Dependencies
├── Dockerfile          # Optional
└── README.md
```

### app.py for HF Spaces:
```python
import gradio as gr
import sys
import os

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.main import app
import uvicorn

# Create Gradio interface
def create_gradio_app():
    def chat_interface(message):
        # Call your FastAPI endpoint
        import requests
        try:
            response = requests.post(
                "http://localhost:8000/chat",
                json={"message": message},
                timeout=30
            )
            return response.json().get("response", "Error")
        except:
            return "Service starting, please wait..."

    demo = gr.Interface(
        fn=chat_interface,
        inputs=gr.Textbox(label="Your Message", placeholder="Type your message..."),
        outputs=gr.Textbox(label="Response"),
        title="LLM Chat API",
        description="Chat with AI that learns from your teachings"
    )
    return demo

# Run FastAPI in background
import threading
def run_api():
    uvicorn.run(app, host="0.0.0.0", port=8000)

threading.Thread(target=run_api, daemon=True).start()

# Launch Gradio
demo = create_gradio_app()
demo.launch(server_name="0.0.0.0", server_port=7860)
```

### Dockerfile for HF Spaces:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/
COPY app.py .

# Expose ports
EXPOSE 7860 8000

# Run both services
CMD ["python", "app.py"]
```

---

## 2. Railway

### railway.json:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Procfile:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Environment Variables (Railway Dashboard):
```
API_HOST=0.0.0.0
API_PORT=$PORT
LOG_LEVEL=INFO
```

---

## 3. Render

### render.yaml:
```yaml
services:
  - type: web
    name: llm-chat-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: API_HOST
        value: 0.0.0.0
      - key: API_PORT
        sync: false
        fromService:
          type: web
          name: llm-chat-api
          property: port
```

### Procfile (for Render):
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## 4. Replicate

### replicate.yaml:
```yaml
image: your-username/llm-chat
build:
  - RUN pip install -r requirements.txt
  - COPY app /app
predict:
  python: |
    from app.main import app
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Or use Replicate Python SDK:
```python
import replicate

# Create model
model = replicate.models.create(
    owner="your-username",
    name="llm-chat-api"
)

# Deploy
deployment = replicate.deployments.create(
    name="llm-chat-api",
    model="your-username/llm-chat-api",
    hardware="gpu-t4"
)

# Use
output = replicate.run(
    f"{deployment.owner}/{deployment.name}",
    input={"message": "Hello"}
)
```

---

## 5. RunPod Template

### Create RunPod Template:

**1. Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**2. RunPod Startup Script:**
```bash
#!/bin/bash
cd /workspace
git clone YOUR_REPO_URL
cd YOUR_REPO
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 6. Docker Hub (Generic)

### Build and Push:
```bash
# Build
docker build -t your-username/llm-chat-api .

# Push
docker push your-username/llm-chat-api

# Run anywhere
docker run -p 8000:8000 your-username/llm-chat-api
```

---

## 7. AWS/Azure/GCP (Advanced)

### AWS Lambda (Serverless):
```python
# lambda_handler.py
from app.main import app
from mangum import Mangum

handler = Mangum(app)

def lambda_handler(event, context):
    return handler(event, context)
```

### Google Cloud Run:
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/llm-chat
gcloud run deploy llm-chat \
  --image gcr.io/PROJECT_ID/llm-chat \
  --platform managed \
  --memory 4Gi \
  --cpu 2
```

---

## Quick Platform Selection

**I want the easiest**: → Hugging Face Spaces (5 min)
**I want cheapest**: → RunPod or Render free tier
**I want managed**: → Replicate or HF Inference API
**I want GitHub integration**: → Railway or Render
**I want full control**: → Current VM method

---

## Platform URLs

- **Hugging Face**: https://huggingface.co/spaces
- **Replicate**: https://replicate.com
- **RunPod**: https://www.runpod.io
- **Railway**: https://railway.app
- **Render**: https://render.com

---

For detailed deployment instructions, see `DEPLOYMENT_GUIDE.md`

