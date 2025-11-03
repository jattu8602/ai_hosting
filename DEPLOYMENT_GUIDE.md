# Complete Deployment Guide - LLM Chat API

This guide covers multiple deployment methods, from self-hosted VMs to managed platforms.

## Table of Contents
1. [Current Deployment (VM Method)](#current-deployment-vm-method)
2. [Easy Deployment Platforms](#easy-deployment-platforms)
3. [Platform Comparison](#platform-comparison)
4. [Step-by-Step Platform Guides](#step-by-step-platform-guides)

---

## Current Deployment (VM Method)

### Prerequisites
- Ubuntu VM (2 vCPU, 4GB+ RAM, 8GB+ disk)
- SSH access to VM
- Python 3.12+, Docker, PM2 installed

### Quick Deployment Steps

#### Step 1: Setup VM
```bash
# Connect to your VM
ssh ubuntu@YOUR_VM_IP

# Run setup script
sudo bash setup.sh
```

#### Step 2: Deploy Application
```bash
# Copy files to VM
scp -r * ubuntu@YOUR_VM_IP:/opt/llm-chat/

# On VM: Generate SSL and start
ssh ubuntu@YOUR_VM_IP
cd /opt/llm-chat
chmod +x ssl/generate-cert.sh
./ssl/generate-cert.sh

# Deploy with PM2 (Recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pm2 start pm2.config.js
pm2 save
pm2 startup
```

#### Step 3: Test API
```bash
curl http://YOUR_VM_IP:8000/health
```

**Pros:**
- Full control
- Customizable
- Cost-effective

**Cons:**
- Requires server management
- Manual setup
- Need to handle scaling

---

## Easy Deployment Platforms

Based on research, here are the easiest platforms for deploying LLM APIs:

### 1. **Hugging Face Inference API** ⭐ (Easiest)
- **Best for**: Quick deployment, free tier available
- **Setup time**: 5-10 minutes
- **Cost**: Free tier + paid options

### 2. **Replicate** ⭐
- **Best for**: One-click deployment
- **Setup time**: 2-5 minutes
- **Cost**: Pay-per-use model

### 3. **RunPod**
- **Best for**: GPU access, affordable
- **Setup time**: 10-15 minutes
- **Cost**: ~$0.20/hour for GPU

### 4. **Hugging Face Spaces**
- **Best for**: Public demos, GitHub integration
- **Setup time**: 10 minutes
- **Cost**: Free tier available

### 5. **Railway**
- **Best for**: Simple deployment, auto-scaling
- **Setup time**: 5 minutes
- **Cost**: Pay-as-you-go

---

## Platform Comparison

| Platform | Setup Time | Cost | Ease | GPU | Best For |
|----------|------------|------|------|-----|----------|
| **Hugging Face Inference** | 5 min | Free/$$ | ⭐⭐⭐⭐⭐ | ✅ | Quick start |
| **Replicate** | 2 min | Pay-per-use | ⭐⭐⭐⭐⭐ | ✅ | Production |
| **RunPod** | 10 min | $0.20/hr | ⭐⭐⭐⭐ | ✅ | Budget GPU |
| **Hugging Face Spaces** | 10 min | Free | ⭐⭐⭐⭐ | ❌ | Demos |
| **Railway** | 5 min | $$ | ⭐⭐⭐⭐ | ❌ | Simple apps |
| **Self-Hosted VM** | 30 min | $$ | ⭐⭐⭐ | ❌ | Full control |

---

## Step-by-Step Platform Guides

### Option 1: Hugging Face Inference API (Recommended for Easiest)

Hugging Face provides managed inference endpoints - the easiest way to deploy.

#### Advantages:
- Zero infrastructure management
- Auto-scaling
- Free tier available
- Built-in monitoring

#### Steps:

**1. Upload Model to Hugging Face Hub:**
```bash
# Install huggingface_hub
pip install huggingface_hub

# Login
huggingface-cli login

# Upload your fine-tuned model (optional)
# Or use existing model: gpt2
```

**2. Create Inference Endpoint (Web UI):**
- Go to https://huggingface.co/spaces
- Click "Create new Space"
- Choose "Docker" type
- Upload your code
- HF handles everything!

**3. Access via API:**
```python
import requests

API_URL = "https://your-endpoint.hf.space/api/predict"
response = requests.post(API_URL, json={"data": "Hello"})
```

**4. Or Use Hugging Face Inference Endpoints:**
```bash
# Create endpoint via CLI
huggingface-cli inference create \
  --repository-id "gpt2" \
  --type "public" \
  --framework "pytorch" \
  --task "text-generation"
```

**Cost**: Free tier: 30k requests/month, then pay-as-you-go

---

### Option 2: Replicate (One-Click Deployment)

Replicate makes deployment extremely simple with pre-built containers.

#### Steps:

**1. Create Replicate Account:**
- Sign up at https://replicate.com

**2. Deploy Model:**
```python
import replicate

# Deploy your model
model = replicate.models.create(
    owner="your-username",
    name="llm-chat",
    visibility="public"
)

# Create a version
version = replicate.models.versions.create(
    owner="your-username",
    name="llm-chat",
    version={
        "weights": "path/to/model",
        "config": "config.yaml"
    }
)
```

**3. Use via API:**
```bash
curl -X POST https://api.replicate.com/v1/predictions \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "version": "your-version-id",
    "input": {"prompt": "Hello"}
  }'
```

**Cost**: Pay-per-second of compute time (~$0.0001/sec)

---

### Option 3: RunPod (Budget GPU Hosting)

RunPod offers affordable GPU instances perfect for LLM hosting.

#### Steps:

**1. Create RunPod Account:**
- Sign up at https://www.runpod.io

**2. Launch GPU Pod:**
```bash
# Via web UI or API
# Choose: RTX 3090, 24GB VRAM ($0.20/hr)
# Template: PyTorch 2.1
```

**3. Deploy Your Code:**
```bash
# SSH into pod
ssh root@YOUR_POD_IP

# Clone your repo
git clone YOUR_REPO
cd YOUR_REPO

# Install and run
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**4. Access API:**
- RunPod provides public URLs
- Or use your pod's IP directly

**Cost**: $0.20/hour for RTX 3090 (~$144/month)

---

### Option 4: Hugging Face Spaces (Free Demo)

Perfect for creating public demos.

#### Steps:

**1. Create Space:**
- Go to https://huggingface.co/spaces
- Click "New Space"
- Name: `your-username/llm-chat-api`
- SDK: Docker
- Visibility: Public/Private

**2. Add Files:**
```
app.py          # Your FastAPI app
requirements.txt
Dockerfile
README.md
```

**3. app.py Example:**
```python
from fastapi import FastAPI
from transformers import pipeline

app = FastAPI()
generator = pipeline('text-generation', model='gpt2')

@app.post("/chat")
def chat(message: str):
    result = generator(message, max_length=50)[0]['generated_text']
    return {"response": result}
```

**4. Deploy:**
- Push to GitHub
- Connect to HF Spaces
- Auto-deploys!

**Cost**: Free (with resource limits)

---

### Option 5: Railway (Simple Cloud Deployment)

Railway automates deployment from GitHub.

#### Steps:

**1. Create Railway Account:**
- Sign up at https://railway.app (GitHub login)

**2. Create New Project:**
- Click "New Project"
- Select "Deploy from GitHub repo"
- Choose your repository

**3. Configure:**
- Railway auto-detects Python
- Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Add environment variables if needed

**4. Deploy:**
- Railway builds and deploys automatically
- Get public URL: `https://your-app.railway.app`

**Cost**: $5/month starter, pay-as-you-go after

---

### Option 6: Render (Another Simple Option)

Similar to Railway, very easy deployment.

#### Steps:

**1. Create Render Account:**
- Sign up at https://render.com

**2. Create Web Service:**
- Connect GitHub repo
- Choose "Web Service"
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**3. Deploy:**
- Render handles the rest
- Get URL: `https://your-app.onrender.com`

**Cost**: Free tier (spins down after inactivity), $7/month always-on

---

## Recommended Deployment Strategy

### For Quick Testing/Demo:
→ **Hugging Face Spaces** (Free, 5 minutes)

### For Production API:
→ **Replicate** or **Hugging Face Inference Endpoints** (Managed, scalable)

### For Budget Production:
→ **RunPod** ($0.20/hr GPU instances)

### For Full Control:
→ **Self-Hosted VM** (Current method)

### For Easiest Deployment:
→ **Railway** or **Render** (GitHub → Deploy, done!)

---

## Platform-Specific Setup Files

### For Hugging Face Spaces

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ ./app/

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `app.py` (for HF Spaces):
```python
import gradio as gr
from transformers import pipeline

generator = pipeline('text-generation', model='gpt2')

def chat(message):
    result = generator(message, max_length=50, do_sample=True)[0]['generated_text']
    # Clean response
    response = result.replace(message, "").strip()[:100]
    return response or "Hello!"

iface = gr.Interface(
    fn=chat,
    inputs="text",
    outputs="text",
    title="LLM Chat API"
)
iface.launch(server_name="0.0.0.0", server_port=7860)
```

### For Railway/Render

Add `Procfile`:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Or in `package.json`:
```json
{
  "scripts": {
    "start": "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
  }
}
```

---

## Comparison: Current vs. Managed Platforms

| Feature | Current (VM) | HF Spaces | Replicate | RunPod |
|---------|--------------|-----------|-----------|--------|
| Setup Time | 30 min | 5 min | 2 min | 10 min |
| Cost/Month | $10-50 | Free/$$ | Pay-per-use | $144 |
| Customization | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Ease of Use | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Scalability | Manual | Auto | Auto | Manual |
| GPU Access | ❌ | ✅ | ✅ | ✅ |
| Learning/RAG | ✅ | ✅ | ✅ | ✅ |

---

## Quick Start: Easiest Method (Hugging Face Spaces)

1. **Fork this repo** or upload files
2. **Go to**: https://huggingface.co/spaces
3. **Click**: "New Space"
4. **Name**: `your-username/llm-chat`
5. **SDK**: Docker
6. **Upload**: Your files
7. **Deploy**: Automatic!
8. **Access**: `https://your-username-llm-chat.hf.space`

**Done in 5 minutes!**

---

## Migration Guide: VM → Managed Platform

### From VM to Hugging Face Spaces:

1. Create Space
2. Upload `app/` folder
3. Upload `requirements.txt`
4. Create `Dockerfile` (provided above)
5. Push to GitHub
6. Connect Space to repo
7. Done!

### From VM to Replicate:

1. Create Replicate account
2. Use their CLI or web UI
3. Upload model weights
4. Configure API endpoint
5. Done!

---

## Cost Analysis

### Self-Hosted VM:
- VM: $10-50/month
- Maintenance: Manual
- **Total: ~$20-50/month**

### Hugging Face Spaces:
- Free tier: Unlimited (with limits)
- Pro: $9/month
- **Total: $0-9/month**

### Replicate:
- Pay-per-second
- ~$0.0001/sec
- **Total: ~$5-30/month** (depending on usage)

### RunPod:
- GPU: $0.20/hour
- **Total: ~$144/month** (always-on)

---

## Next Steps

1. **Choose platform** based on your needs
2. **Follow platform guide** above
3. **Test API endpoints**
4. **Scale as needed**

For questions or issues, refer to platform-specific documentation or this repo's issues.

---

## Additional Resources

- **Hugging Face**: https://huggingface.co/docs
- **Replicate Docs**: https://replicate.com/docs
- **RunPod Docs**: https://docs.runpod.io
- **Railway Docs**: https://docs.railway.app
- **Render Docs**: https://render.com/docs

