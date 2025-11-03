"""
Embedding model for RAG (Retrieval Augmented Generation)
Uses sentence-transformers for generating embeddings
"""
from sentence_transformers import SentenceTransformer
import logging
from app.config import EMBEDDING_MODEL, MODEL_CACHE_DIR

logger = logging.getLogger(__name__)

class EmbeddingModel:
    """Lightweight embedding model for knowledge retrieval"""

    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingModel, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._model is None:
            self.load_model()

    def load_model(self):
        """Load the embedding model"""
        try:
            logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
            cache_dir = str(MODEL_CACHE_DIR / "embeddings")
            self._model = SentenceTransformer(
                EMBEDDING_MODEL,
                cache_folder=cache_dir
            )
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise

    def encode(self, texts):
        """
        Generate embeddings for texts

        Args:
            texts: Single string or list of strings

        Returns:
            numpy array of embeddings
        """
        if self._model is None:
            self.load_model()

        # Handle single string
        if isinstance(texts, str):
            texts = [texts]

        return self._model.encode(texts, show_progress_bar=False)

