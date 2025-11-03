"""
Chat handler that combines model inference with RAG knowledge retrieval
"""
import logging
import threading
from typing import List, Dict, Optional
from app.model import Phi2Model
from app.knowledge import KnowledgeStore

logger = logging.getLogger(__name__)

class ChatHandler:
    """Handles chat interactions with learning capabilities"""

    def __init__(self):
        self.model = Phi2Model()
        self.knowledge_store = KnowledgeStore()
        self.conversation_history: List[Dict] = []

    def chat(self, user_message: str, conversation_id: Optional[str] = None) -> Dict:
        """
        Process chat message with RAG - fast synchronous retrieval, async learning

        Args:
            user_message: User's message
            conversation_id: Optional conversation ID for context

        Returns:
            Dictionary with response and metadata
        """
        try:
            # Fast synchronous knowledge retrieval (should be instant)
            relevant_knowledge = self.knowledge_store.retrieve_relevant_knowledge(
                user_message,
                top_k=2  # Limit to 2 for speed
            )

            # Build context silently (no metadata tags that reveal knowledge source)
            context = ""
            if relevant_knowledge:
                # Just use the text, don't reveal it's learned knowledge
                context_parts = [item['text'] for item in relevant_knowledge[:2]]
                context = " ".join(context_parts)
                logger.debug(f"Using {len(relevant_knowledge)} knowledge items (silently)")

            # Generate response (fast with max 50 tokens)
            response = self.model.generate(
                prompt=user_message,
                context=context,
                max_tokens=50  # Hard limit for speed
            )

            # Background learning - fire and forget, doesn't block response
            def store_conversation():
                try:
                    self.conversation_history.append({
                        "user": user_message,
                        "assistant": response,
                        "knowledge_used": len(relevant_knowledge)
                    })
                except:
                    pass  # Silently fail background task

            # Run in background thread - don't wait
            import threading
            threading.Thread(target=store_conversation, daemon=True).start()

            return {
                "response": response,
                "knowledge_used": len(relevant_knowledge),
                "conversation_id": conversation_id
            }

        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return {
                "response": "Sorry, I encountered an error.",
                "error": True
            }

    def teach(self, knowledge: str, topic: str = "") -> Dict:
        """
        Store new knowledge - async background storage for speed

        Args:
            knowledge: The knowledge to store
            topic: Optional topic/category

        Returns:
            Dictionary with success status and message
        """
        try:
            # Validate first (fast check)
            if not knowledge or len(knowledge.strip()) < 10:
                return {
                    "success": False,
                    "message": "Knowledge too short (minimum 10 characters)"
                }

            # Async store - fire and forget for instant response
            def store_async():
                try:
                    self.knowledge_store.store_knowledge(knowledge, topic)
                    logger.info(f"Knowledge stored (background): {topic if topic else 'General'}")
                except Exception as e:
                    logger.error(f"Background knowledge storage failed: {e}")

            # Store in background thread - don't wait
            threading.Thread(target=store_async, daemon=True).start()

            # Return immediately - storage happens in background
            return {
                "success": True,
                "message": "Knowledge will be stored in background"
            }

        except Exception as e:
            logger.error(f"Error in teach: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")

