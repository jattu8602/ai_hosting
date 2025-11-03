"""
Configuration settings for the LLM Chat System
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MODEL_CACHE_DIR = DATA_DIR / "models"
KNOWLEDGE_DB_DIR = DATA_DIR / "chromadb"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
KNOWLEDGE_DB_DIR.mkdir(parents=True, exist_ok=True)

# Model Configuration
MODEL_NAME = "gpt2"  # Small, fast model (124M params, ~500MB) perfect for simple chatbot
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
QUANTIZATION_BITS = 4  # 4-bit quantization for memory efficiency

# Generation Parameters
MAX_NEW_TOKENS = 50  # Very short responses for speed (2-5 seconds)
TEMPERATURE = 0.7
TOP_P = 0.9
TOP_K = 50

# RAG Configuration
RAG_SIMILARITY_THRESHOLD = 0.7
MAX_RETRIEVED_DOCS = 3
KNOWLEDGE_COLLECTION_NAME = "user_knowledge"

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
SSL_CERT_PATH = BASE_DIR / "ssl" / "server.crt"
SSL_KEY_PATH = BASE_DIR / "ssl" / "server.key"

# CORS Configuration
ALLOWED_ORIGINS = ["*"]  # Public access for now

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

