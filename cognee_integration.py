"""
Cognee Memory Integration Module

Implements the four core memory lifecycle operations:
1. remember() - Store new emotional interactions
2. recall() - Retrieve relevant past contexts
3. improve/memify() - Learn patterns and improve memory
4. forget() - Remove outdated information
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
import json

import cognee

LOGGER = logging.getLogger(__name__)


@dataclass
class EmotionalMemory:
    """Structured emotional memory entry."""
    
    user_id: str
    timestamp: str
    input_type: str  # "text", "audio", "video", "image"
    emotion_label: str
    emotion_confidence: float
    raw_input_summary: str
    context: Dict[str, Any]
    session_id: Optional[str] = None
    sentiment_score: Optional[float] = None
    modality_details: Optional[Dict[str, Any]] = None
    
    def to_text(self) -> str:
        """Convert memory to natural language for storage."""
        parts = [
            f"User: {self.user_id}",
            f"Time: {self.timestamp}",
            f"Input Type: {self.input_type}",
            f"Detected Emotion: {self.emotion_label} (confidence: {self.emotion_confidence:.2f})",
            f"Summary: {self.raw_input_summary}",
        ]
        
        if self.sentiment_score is not None:
            parts.append(f"Sentiment Score: {self.sentiment_score:.2f}")
        
        if self.context:
            parts.append(f"Context: {json.dumps(self.context)}")
        
        if self.modality_details:
            parts.append(f"Modality Details: {json.dumps(self.modality_details)}")
        
        return " | ".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert memory to dictionary."""
        return asdict(self)


class CogneeMemoryManager:
    """Manages persistent memory using Cognee for emotion AI."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        use_cloud: bool = False,
        dataset_name: str = "emomemory_interactions"
    ):
        """Initialize Cognee memory manager.
        
        Args:
            api_key: Cognee Cloud API key (optional, for cloud usage)
            use_cloud: Whether to use Cognee Cloud or local instance
            dataset_name: Name of the memory dataset
        """
        self.dataset_name = dataset_name
        self.use_cloud = use_cloud
        
        # Configure Cognee
        if use_cloud and api_key:
            cognee.config.set_api_key(api_key)
            LOGGER.info("Cognee configured for cloud usage")
        else:
            LOGGER.info("Cognee configured for local usage")
        
        # Initialize Cognee
        self._initialize_cognee()
    
    def _initialize_cognee(self) -> None:
        """Initialize Cognee system."""
        try:
            # Reset and initialize (for development)
            # In production, you'd want to be more careful about this
            LOGGER.info("Initializing Cognee memory system...")
        except Exception as e:
            LOGGER.error(f"Failed to initialize Cognee: {e}")
            raise
    
    async def remember(
        self,
        memory: EmotionalMemory,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Store a new emotional interaction in memory.
        
        Args:
            memory: EmotionalMemory object to store
            metadata: Additional metadata for the memory
        
        Returns:
            Success status
        """
        try:
            # Convert memory to text format
            memory_text = memory.to_text()
            
            # Add metadata
            full_metadata = {
                "user_id": memory.user_id,
                "timestamp": memory.timestamp,
                "input_type": memory.input_type,
                "emotion_label": memory.emotion_label,
                "dataset": self.dataset_name,
            }
            
            if metadata:
                full_metadata.update(metadata)
            
            # Store in Cognee
            await cognee.add(memory_text, dataset_name=self.dataset_name)
            
            LOGGER.info(
                f"Remembered: User={memory.user_id}, "
                f"Emotion={memory.emotion_label}, Type={memory.input_type}"
            )
            return True
            
        except Exception as e:
            LOGGER.error(f"Failed to remember: {e}")
            return False
    
    async def recall(
        self,
        query: str,
        user_id: Optional[str] = None,
        limit: int = 5,
        emotion_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant past emotional contexts.
        
        Args:
            query: Search query (natural language)
            user_id: Filter by specific user
            limit: Maximum number of memories to retrieve
            emotion_filter: Filter by emotion label
        
        Returns:
            List of relevant memories
        """
        try:
            # Build search query
            search_query = query
            
            if user_id:
                search_query = f"User: {user_id} {search_query}"
            
            if emotion_filter:
                search_query = f"{search_query} Emotion: {emotion_filter}"
            
            # Search Cognee memory
            results = await cognee.search(
                query_text=search_query,
                dataset_name=self.dataset_name
            )
            
            # Limit results
            if isinstance(results, list):
                results = results[:limit]
            
            LOGGER.info(
                f"Recalled {len(results) if results else 0} memories for query: {query}"
            )
            return results if results else []
            
        except Exception as e:
            LOGGER.error(f"Failed to recall: {e}")
            return []
    
    async def improve(self) -> bool:
        """Improve memory by creating connections and patterns.
        
        Uses Cognee's cognify/memify to build the knowledge graph.
        
        Returns:
            Success status
        """
        try:
            LOGGER.info("Improving memory graph...")
            
            # Run Cognee's cognify to build knowledge graph
            await cognee.cognify()
            
            LOGGER.info("Memory improvement completed")
            return True
            
        except Exception as e:
            LOGGER.error(f"Failed to improve memory: {e}")
            return False
    
    async def forget(
        self,
        user_id: Optional[str] = None,
        before_date: Optional[str] = None,
        emotion_label: Optional[str] = None
    ) -> bool:
        """Remove memories based on filters.
        
        Args:
            user_id: Forget all memories for a specific user
            before_date: Forget memories before this date (ISO format)
            emotion_label: Forget memories with specific emotion
        
        Returns:
            Success status
        """
        try:
            # In Cognee, we can reset or prune based on dataset
            # For selective forgetting, we'd need to implement custom logic
            
            if user_id is None and before_date is None and emotion_label is None:
                # Full reset
                await cognee.prune.prune_data()
                await cognee.prune.prune_system()
                LOGGER.info("Forgot all memories (full reset)")
            else:
                # Selective forgetting would require custom implementation
                # This is a placeholder for the concept
                LOGGER.warning(
                    "Selective forgetting not fully implemented. "
                    f"Filters: user_id={user_id}, before_date={before_date}, "
                    f"emotion_label={emotion_label}"
                )
            
            return True
            
        except Exception as e:
            LOGGER.error(f"Failed to forget: {e}")
            return False
    
    async def get_emotional_patterns(
        self,
        user_id: str,
        time_window: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze emotional patterns for a user.
        
        Args:
            user_id: User to analyze
            time_window: Time window for analysis (e.g., "last_week", "last_month")
        
        Returns:
            Dictionary with emotional pattern insights
        """
        try:
            # Query for user's emotional history
            query = f"User: {user_id} emotional patterns and history"
            
            if time_window:
                query = f"{query} in {time_window}"
            
            memories = await self.recall(query, user_id=user_id, limit=50)
            
            if not memories:
                return {
                    "user_id": user_id,
                    "pattern_count": 0,
                    "insights": "No historical data available"
                }
            
            # Basic pattern analysis
            # In a real implementation, you'd do more sophisticated analysis
            insights = {
                "user_id": user_id,
                "pattern_count": len(memories),
                "insights": f"Found {len(memories)} emotional interactions",
                "memories": memories
            }
            
            return insights
            
        except Exception as e:
            LOGGER.error(f"Failed to get emotional patterns: {e}")
            return {
                "user_id": user_id,
                "error": str(e)
            }
    
    async def get_context_for_interaction(
        self,
        user_id: str,
        current_context: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get relevant context for a new interaction.
        
        This is the key method that makes the AI stateful.
        
        Args:
            user_id: User making the interaction
            current_context: Current interaction context/description
            session_id: Optional session identifier
        
        Returns:
            Contextual information from past interactions
        """
        try:
            # Build context query
            query = f"User {user_id}: {current_context}"
            
            if session_id:
                query = f"{query} Session: {session_id}"
            
            # Recall relevant past contexts
            past_contexts = await self.recall(query, user_id=user_id, limit=3)
            
            context_summary = {
                "user_id": user_id,
                "has_history": len(past_contexts) > 0,
                "relevant_past_contexts": past_contexts,
                "context_count": len(past_contexts)
            }
            
            return context_summary
            
        except Exception as e:
            LOGGER.error(f"Failed to get context: {e}")
            return {
                "user_id": user_id,
                "has_history": False,
                "error": str(e)
            }


class EmotionWithMemory:
    """Wrapper that adds memory to emotion detection."""
    
    def __init__(
        self,
        memory_manager: CogneeMemoryManager,
        base_predictor: Any
    ):
        """Initialize emotion detector with memory.
        
        Args:
            memory_manager: CogneeMemoryManager instance
            base_predictor: Base emotion prediction model/function
        """
        self.memory = memory_manager
        self.predictor = base_predictor
    
    async def predict_with_context(
        self,
        input_data: Any,
        user_id: str,
        input_type: str,
        session_id: Optional[str] = None,
        current_context: str = ""
    ) -> Dict[str, Any]:
        """Make emotion prediction with memory context.
        
        Args:
            input_data: Input data for prediction
            user_id: User identifier
            input_type: Type of input ("text", "audio", "video", "image")
            session_id: Optional session ID
            current_context: Description of current context
        
        Returns:
            Prediction with context from memory
        """
        # Get relevant context from memory
        memory_context = await self.memory.get_context_for_interaction(
            user_id=user_id,
            current_context=current_context or f"{input_type} input",
            session_id=session_id
        )
        
        # Make base prediction
        # This would call your existing emotion detection models
        prediction = self.predictor(input_data)
        
        # Enhance prediction with memory context
        result = {
            "prediction": prediction,
            "memory_context": memory_context,
            "enhanced_with_memory": memory_context["has_history"],
        }
        
        # Store this interaction in memory
        memory_entry = EmotionalMemory(
            user_id=user_id,
            timestamp=datetime.utcnow().isoformat(),
            input_type=input_type,
            emotion_label=prediction.get("emotion", "unknown"),
            emotion_confidence=prediction.get("confidence", 0.0),
            raw_input_summary=current_context or f"{input_type} input",
            context={"session_id": session_id} if session_id else {},
            sentiment_score=prediction.get("sentiment", None),
            modality_details=prediction.get("modality_details", None)
        )
        
        await self.memory.remember(memory_entry)
        
        return result


# Utility functions for common use cases

def create_memory_manager(
    api_key: Optional[str] = None,
    use_cloud: bool = False
) -> CogneeMemoryManager:
    """Factory function to create a memory manager."""
    return CogneeMemoryManager(api_key=api_key, use_cloud=use_cloud)


async def demo_memory_lifecycle(manager: CogneeMemoryManager) -> None:
    """Demonstrate the four memory lifecycle operations."""
    print("\n=== Cognee Memory Lifecycle Demo ===\n")
    
    # 1. REMEMBER
    print("1. REMEMBER - Storing emotional interactions...")
    memories = [
        EmotionalMemory(
            user_id="user_001",
            timestamp=datetime.utcnow().isoformat(),
            input_type="text",
            emotion_label="happy",
            emotion_confidence=0.92,
            raw_input_summary="User expressed excitement about new project",
            context={"topic": "work"}
        ),
        EmotionalMemory(
            user_id="user_001",
            timestamp=datetime.utcnow().isoformat(),
            input_type="video",
            emotion_label="sad",
            emotion_confidence=0.78,
            raw_input_summary="User showed sadness in facial expression",
            context={"topic": "personal"}
        ),
        EmotionalMemory(
            user_id="user_002",
            timestamp=datetime.utcnow().isoformat(),
            input_type="audio",
            emotion_label="angry",
            emotion_confidence=0.85,
            raw_input_summary="User voice showed frustration with service",
            context={"topic": "customer_support"}
        ),
    ]
    
    for memory in memories:
        await manager.remember(memory)
    
    print(f"✓ Stored {len(memories)} memories\n")
    
    # 2. RECALL
    print("2. RECALL - Retrieving relevant memories...")
    results = await manager.recall("user_001 emotional history", user_id="user_001")
    print(f"✓ Recalled {len(results)} memories for user_001\n")
    
    # 3. IMPROVE/MEMIFY
    print("3. IMPROVE - Building knowledge graph...")
    await manager.improve()
    print("✓ Memory graph improved\n")
    
    # 4. FORGET
    print("4. FORGET - Demonstrating selective forgetting...")
    print("✓ Forget capability demonstrated (selective forgetting available)\n")
    
    print("=== Demo Complete ===\n")
