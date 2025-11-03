"""
Knowledge storage and retrieval using ChromaDB
Implements RAG (Retrieval Augmented Generation) for learning from user teachings
"""
import chromadb
from chromadb.config import Settings
import logging
from typing import List, Dict, Optional
from app.config import KNOWLEDGE_DB_DIR, KNOWLEDGE_COLLECTION_NAME, RAG_SIMILARITY_THRESHOLD, MAX_RETRIEVED_DOCS
from app.embeddings import EmbeddingModel

logger = logging.getLogger(__name__)

class KnowledgeStore:
    """Manages knowledge storage and retrieval using ChromaDB"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KnowledgeStore, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.embedding_model = EmbeddingModel()
            self.client = None
            self.collection = None
            self._initialize_db()

    def _initialize_db(self):
        """Initialize ChromaDB client and collection"""
        try:
            logger.info("Initializing ChromaDB...")
            self.client = chromadb.PersistentClient(
                path=str(KNOWLEDGE_DB_DIR),
                settings=Settings(anonymized_telemetry=False)
            )

            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=KNOWLEDGE_COLLECTION_NAME,
                metadata={"description": "User knowledge storage for RAG"}
            )

            logger.info(f"ChromaDB initialized. Collection size: {self.collection.count()}")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
            raise

    def validate_knowledge(self, knowledge: str, topic: str = "") -> bool:
        """
        Basic validation for new knowledge

        Args:
            knowledge: The knowledge text to validate
            topic: Optional topic/category

        Returns:
            bool: True if valid, False otherwise
        """
        if not knowledge or len(knowledge.strip()) < 10:
            logger.warning("Knowledge too short or empty")
            return False

        if len(knowledge) > 5000:  # Reasonable limit
            logger.warning("Knowledge too long")
            return False

        return True

    def store_knowledge(self, knowledge: str, topic: str = "", metadata: Optional[Dict] = None) -> bool:
        """
        Store new knowledge with validation

        Args:
            knowledge: The knowledge text to store
            topic: Topic/category (e.g., "chess")
            metadata: Additional metadata dictionary

        Returns:
            bool: True if stored successfully
        """
        if not self.validate_knowledge(knowledge, topic):
            return False

        try:
            # Generate embedding
            embedding = self.embedding_model.encode(knowledge)

            # Prepare metadata
            doc_metadata = {"topic": topic} if topic else {}
            if metadata:
                doc_metadata.update(metadata)

            # Generate unique ID
            import uuid
            doc_id = str(uuid.uuid4())

            # Store in ChromaDB
            self.collection.add(
                ids=[doc_id],
                embeddings=[embedding.tolist()],
                documents=[knowledge],
                metadatas=[doc_metadata]
            )

            logger.info(f"Knowledge stored successfully. Topic: {topic}")
            return True

        except Exception as e:
            logger.error(f"Error storing knowledge: {e}")
            return False

    def retrieve_relevant_knowledge(self, query: str, top_k: int = 2) -> List[Dict]:
        """
        Retrieve relevant knowledge based on query similarity

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of dictionaries with 'text', 'topic', and 'score' keys
        """
        if self.collection.count() == 0:
            logger.info("No knowledge in database")
            return []

        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query)

            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=min(top_k, self.collection.count()),
                include=["documents", "metadatas", "distances"]
            )

            # Format results
            retrieved_knowledge = []
            if results['documents'] and len(results['documents'][0]) > 0:
                for i, doc in enumerate(results['documents'][0]):
                    # Convert distance to similarity score (ChromaDB returns L2 distance)
                    # Lower distance = higher similarity
                    distance = results['distances'][0][i]
                    similarity = 1 / (1 + distance)  # Simple conversion

                    if similarity >= RAG_SIMILARITY_THRESHOLD:
                        retrieved_knowledge.append({
                            'text': doc,
                            'topic': results['metadatas'][0][i].get('topic', ''),
                            'score': similarity
                        })

            logger.info(f"Retrieved {len(retrieved_knowledge)} relevant knowledge items")
            return retrieved_knowledge

        except Exception as e:
            logger.error(f"Error retrieving knowledge: {e}")
            return []

    def get_all_knowledge(self, topic: Optional[str] = None) -> List[Dict]:
        """
        Get all stored knowledge, optionally filtered by topic

        Args:
            topic: Optional topic filter

        Returns:
            List of knowledge dictionaries
        """
        try:
            if topic:
                results = self.collection.get(
                    where={"topic": topic},
                    include=["documents", "metadatas"]
                )
            else:
                results = self.collection.get(
                    include=["documents", "metadatas"]
                )

            knowledge_list = []
            if results['ids']:
                for i, doc_id in enumerate(results['ids']):
                    knowledge_list.append({
                        'id': doc_id,
                        'text': results['documents'][i],
                        'topic': results['metadatas'][i].get('topic', ''),
                        'metadata': results['metadatas'][i]
                    })

            return knowledge_list
        except Exception as e:
            logger.error(f"Error getting all knowledge: {e}")
            return []

