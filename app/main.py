"""
FastAPI application for LLM Chat System
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import logging
from typing import Optional
import uvicorn

from app.chat import ChatHandler
from app.config import API_HOST, API_PORT, SSL_CERT_PATH, SSL_KEY_PATH, ALLOWED_ORIGINS, LOG_LEVEL

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="LLM Chat API",
    description="Chat API with learning capabilities using Phi-2 and RAG",
    version="1.0.0"
)

# CORS middleware (public access for now)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chat handler (singleton pattern used internally)
chat_handler = ChatHandler()

# Request/Response Models
class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID")

class ChatResponse(BaseModel):
    response: str
    knowledge_used: int = 0
    conversation_id: Optional[str] = None

class TeachRequest(BaseModel):
    knowledge: str = Field(..., description="Knowledge to store", min_length=10)
    topic: Optional[str] = Field(None, description="Topic/category (e.g., 'chess')")

class TeachResponse(BaseModel):
    success: bool
    message: str

# Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "LLM Chat API"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Chat with the model

    The model will retrieve relevant learned knowledge and use it in the response.
    """
    try:
        result = chat_handler.chat(
            user_message=request.message,
            conversation_id=request.conversation_id
        )

        if result.get("error"):
            raise HTTPException(status_code=500, detail=result.get("response"))

        return ChatResponse(
            response=result["response"],
            knowledge_used=result.get("knowledge_used", 0),
            conversation_id=result.get("conversation_id")
        )

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/teach", response_model=TeachResponse)
async def teach_endpoint(request: TeachRequest):
    """
    Teach the model new knowledge

    Example:
    - knowledge: "In chess, the king can move one square in any direction."
    - topic: "chess"

    Later, when someone asks about chess, this knowledge will be retrieved and used.
    """
    try:
        result = chat_handler.teach(
            knowledge=request.knowledge,
            topic=request.topic or ""
        )

        return TeachResponse(
            success=result["success"],
            message=result["message"]
        )

    except Exception as e:
        logger.error(f"Error in teach endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/knowledge")
async def get_knowledge(topic: Optional[str] = None):
    """
    Get all stored knowledge, optionally filtered by topic
    """
    try:
        knowledge_list = chat_handler.knowledge_store.get_all_knowledge(topic=topic)
        return {
            "count": len(knowledge_list),
            "knowledge": knowledge_list
        }
    except Exception as e:
        logger.error(f"Error getting knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Check if SSL files exist
    use_ssl = SSL_CERT_PATH.exists() and SSL_KEY_PATH.exists()

    uvicorn.run(
        "app.main:app",
        host=API_HOST,
        port=API_PORT,
        ssl_certfile=str(SSL_CERT_PATH) if use_ssl else None,
        ssl_keyfile=str(SSL_KEY_PATH) if use_ssl else None,
        log_level=LOG_LEVEL.lower()
    )

