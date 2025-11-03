# Multi-stage Dockerfile for optimized LLM Chat System

# Stage 1: Base image with Python
FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Install Python dependencies
FROM base as dependencies

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 3: Final image
FROM dependencies as final

# Copy application code
COPY app/ ./app/
COPY ssl/ ./ssl/

# Create data directory
RUN mkdir -p /app/data/models /app/data/chromadb

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV TRANSFORMERS_CACHE=/app/data/models
ENV HF_HOME=/app/data/models

# Expose ports
EXPOSE 8000 443

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Copy run script
COPY run.sh ./
RUN chmod +x run.sh

# Run the application
CMD ["./run.sh"]

