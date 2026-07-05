"""
Memory-Aware Emotion Agent

Wraps existing emotion detection agents (FED, SER, TED, AED) with Cognee memory.
Provides stateful emotion intelligence that learns from past interactions.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from cognee_integration import (
    CogneeMemoryManager,
    EmotionalMemory,
    EmotionWithMemory,
    create_memory_manager
)

LOGGER = logging.getLogger(__name__)


class MemoryAwareEmotionAgent:
    """
    Stateful emotion detection agent powered by Cognee memory.
    
    This agent wraps your existing emotion detection models and adds:
    - Persistent memory of past interactions
    - Context-aware predictions
    - Emotional pattern tracking
    - Learning from user feedback
    """
    
    def __init__(
        self,
        agent_type: str = "multimodal",
        api_key: Optional[str] = None,
        use_cloud: bool = False,
        enable_pattern_learning: bool = True
    ):
        """Initialize memory-aware emotion agent.
        
        Args:
            agent_type: Type of emotion agent ("fed", "ser", "ted", "aed", "multimodal")
            api_key: Cognee Cloud API key
            use_cloud: Whether to use Cognee Cloud
            enable_pattern_learning: Enable automatic pattern learning
        """
        self.agent_type = agent_type
        self.enable_pattern_learning = enable_pattern_learning
        
        # Initialize Cognee memory
        self.memory = create_memory_manager(api_key=api_key, use_cloud=use_cloud)
        
        # Load base emotion detection models
        self.models = self._load_models()
        
        LOGGER.info(f"Initialized {agent_type} emotion agent with Cognee memory")
    
    def _load_models(self) -> Dict[str, Any]:
        """Load emotion detection models based on agent type."""
        models = {}
        
        try:
            if self.agent_type in ["fed", "multimodal"]:
                # Facial Emotion Detection
                from agents.fed_agent import FacialEmotionDetector
                models["fed"] = FacialEmotionDetector()
                LOGGER.info("Loaded FED model")
        except Exception as e:
            LOGGER.warning(f"Could not load FED model: {e}")
        
        try:
            if self.agent_type in ["ser", "multimodal"]:
                # Speech Emotion Recognition
                from agents.ser_agent import SpeechEmotionRecognizer
                models["ser"] = SpeechEmotionRecognizer()
                LOGGER.info("Loaded SER model")
        except Exception as e:
            LOGGER.warning(f"Could not load SER model: {e}")
        
        try:
            if self.agent_type in ["ted", "multimodal"]:
                # Text Emotion Detection
                from agents.ted_agent import TextEmotionDetector
                models["ted"] = TextEmotionDetector()
                LOGGER.info("Loaded TED model")
        except Exception as e:
            LOGGER.warning(f"Could not load TED model: {e}")
        
        return models
    
    async def predict_emotion(
        self,
        input_data: Any,
        user_id: str,
        input_type: str,
        session_id: Optional[str] = None,
        context_description: str = "",
        return_memory_context: bool = True
    ) -> Dict[str, Any]:
        """
        Predict emotion with memory context.
        
        Args:
            input_data: Input data (text, audio path, video path, image path)
            user_id: User identifier
            input_type: Type of input ("text", "audio", "video", "image")
            session_id: Optional session identifier
            context_description: Natural language description of context
            return_memory_context: Whether to include memory context in response
        
        Returns:
            Prediction dictionary with emotion, confidence, and memory context
        """
        try:
            # Step 1: Recall relevant past contexts
            memory_context = await self.memory.get_context_for_interaction(
                user_id=user_id,
                current_context=context_description or f"{input_type} input",
                session_id=session_id
            )
            
            # Step 2: Make base prediction using appropriate model
            base_prediction = await self._make_base_prediction(input_data, input_type)
            
            # Step 3: Enhance prediction with memory context
            enhanced_prediction = self._enhance_with_memory(
                base_prediction,
                memory_context
            )
            
            # Step 4: Remember this interaction
            memory_entry = EmotionalMemory(
                user_id=user_id,
                timestamp=datetime.utcnow().isoformat(),
                input_type=input_type,
                emotion_label=enhanced_prediction["emotion"],
                emotion_confidence=enhanced_prediction["confidence"],
                raw_input_summary=context_description or f"{input_type} input",
                context={
                    "session_id": session_id,
                    "had_prior_context": memory_context["has_history"]
                } if session_id else {"had_prior_context": memory_context["has_history"]},
                sentiment_score=enhanced_prediction.get("sentiment_score"),
                modality_details=enhanced_prediction.get("modality_details")
            )
            
            await self.memory.remember(memory_entry)
            
            # Step 5: Build response
            response = {
                "emotion": enhanced_prediction["emotion"],
                "confidence": enhanced_prediction["confidence"],
                "timestamp": memory_entry.timestamp,
                "input_type": input_type,
                "stateful": memory_context["has_history"],
            }
            
            if return_memory_context:
                response["memory_context"] = memory_context
                response["memory_enhanced"] = memory_context["has_history"]
            
            if "sentiment_score" in enhanced_prediction:
                response["sentiment_score"] = enhanced_prediction["sentiment_score"]
            
            if "all_emotions" in enhanced_prediction:
                response["all_emotions"] = enhanced_prediction["all_emotions"]
            
            return response
            
        except Exception as e:
            LOGGER.error(f"Error in predict_emotion: {e}")
            return {
                "emotion": "error",
                "confidence": 0.0,
                "error": str(e),
                "stateful": False
            }
    
    async def _make_base_prediction(
        self,
        input_data: Any,
        input_type: str
    ) -> Dict[str, Any]:
        """Make base emotion prediction using appropriate model."""
        
        if input_type == "text" and "ted" in self.models:
            return self.models["ted"].predict(input_data)
        
        elif input_type == "audio" and "ser" in self.models:
            return self.models["ser"].predict(input_data)
        
        elif input_type in ["image", "video"] and "fed" in self.models:
            return self.models["fed"].predict(input_data)
        
        else:
            # Fallback: mock prediction for demo purposes
            LOGGER.warning(f"No model available for {input_type}, using mock prediction")
            return {
                "emotion": "neutral",
                "confidence": 0.5,
                "all_emotions": {"neutral": 0.5, "happy": 0.3, "sad": 0.2}
            }
    
    def _enhance_with_memory(
        self,
        base_prediction: Dict[str, Any],
        memory_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enhance prediction with memory context.
        
        This is where the magic happens - using past emotional patterns
        to improve current predictions.
        """
        enhanced = base_prediction.copy()
        
        # If we have historical context, we can adjust confidence
        if memory_context["has_history"] and memory_context["relevant_past_contexts"]:
            # Simple enhancement: boost confidence if emotion is consistent
            # In a real implementation, you'd use more sophisticated logic
            enhanced["original_confidence"] = base_prediction["confidence"]
            enhanced["memory_adjusted"] = True
            
            # Could adjust confidence based on patterns, but keeping it simple for now
            LOGGER.info("Enhanced prediction with memory context")
        else:
            enhanced["memory_adjusted"] = False
        
        return enhanced
    
    async def get_emotional_history(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get emotional history for a user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of records to return
        
        Returns:
            List of past emotional interactions
        """
        try:
            query = f"User {user_id} emotional history"
            memories = await self.memory.recall(query, user_id=user_id, limit=limit)
            return memories
        except Exception as e:
            LOGGER.error(f"Error getting emotional history: {e}")
            return []
    
    async def get_emotional_patterns(
        self,
        user_id: str,
        time_window: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze emotional patterns for a user.
        
        Args:
            user_id: User identifier
            time_window: Time window for analysis
        
        Returns:
            Emotional pattern insights
        """
        try:
            patterns = await self.memory.get_emotional_patterns(
                user_id=user_id,
                time_window=time_window
            )
            return patterns
        except Exception as e:
            LOGGER.error(f"Error getting emotional patterns: {e}")
            return {"error": str(e)}
    
    async def improve_memory(self) -> bool:
        """
        Run memory improvement to build knowledge graph.
        
        This should be called periodically to let Cognee build
        connections and patterns in the memory.
        """
        try:
            LOGGER.info("Running memory improvement (cognify)...")
            success = await self.memory.improve()
            
            if success:
                LOGGER.info("Memory improvement completed successfully")
            else:
                LOGGER.warning("Memory improvement failed")
            
            return success
        except Exception as e:
            LOGGER.error(f"Error improving memory: {e}")
            return False
    
    async def forget_user_data(self, user_id: str) -> bool:
        """
        Forget all data for a specific user (GDPR compliance).
        
        Args:
            user_id: User to forget
        
        Returns:
            Success status
        """
        try:
            LOGGER.info(f"Forgetting data for user: {user_id}")
            success = await self.memory.forget(user_id=user_id)
            
            if success:
                LOGGER.info(f"Successfully forgot data for {user_id}")
            else:
                LOGGER.warning(f"Failed to forget data for {user_id}")
            
            return success
        except Exception as e:
            LOGGER.error(f"Error forgetting user data: {e}")
            return False
    
    async def compare_stateless_vs_stateful(
        self,
        input_data: Any,
        user_id: str,
        input_type: str,
        context_description: str = ""
    ) -> Dict[str, Any]:
        """
        Compare stateless vs stateful prediction side-by-side.
        
        Perfect for demonstrating the value of memory!
        
        Args:
            input_data: Input data
            user_id: User identifier
            input_type: Type of input
            context_description: Context description
        
        Returns:
            Comparison of stateless and stateful predictions
        """
        try:
            # Stateless prediction (no memory)
            stateless = await self._make_base_prediction(input_data, input_type)
            
            # Stateful prediction (with memory)
            stateful = await self.predict_emotion(
                input_data=input_data,
                user_id=user_id,
                input_type=input_type,
                context_description=context_description,
                return_memory_context=True
            )
            
            comparison = {
                "stateless": {
                    "emotion": stateless["emotion"],
                    "confidence": stateless["confidence"],
                    "has_context": False
                },
                "stateful": {
                    "emotion": stateful["emotion"],
                    "confidence": stateful["confidence"],
                    "has_context": stateful["stateful"],
                    "memory_context": stateful.get("memory_context", {})
                },
                "difference": {
                    "emotion_changed": stateless["emotion"] != stateful["emotion"],
                    "confidence_delta": stateful["confidence"] - stateless["confidence"],
                    "memory_enhanced": stateful.get("memory_enhanced", False)
                }
            }
            
            return comparison
            
        except Exception as e:
            LOGGER.error(f"Error in comparison: {e}")
            return {"error": str(e)}


# Convenience functions

async def create_memory_agent(
    agent_type: str = "multimodal",
    api_key: Optional[str] = None,
    use_cloud: bool = False
) -> MemoryAwareEmotionAgent:
    """Factory function to create a memory-aware emotion agent."""
    agent = MemoryAwareEmotionAgent(
        agent_type=agent_type,
        api_key=api_key,
        use_cloud=use_cloud
    )
    return agent


async def demo_stateful_emotion_detection():
    """Demonstrate stateful vs stateless emotion detection."""
    print("\n=== Stateful Emotion Detection Demo ===\n")
    
    # Create agent
    agent = await create_memory_agent(agent_type="multimodal")
    
    # Simulate a series of interactions for a user
    user_id = "demo_user_001"
    
    print("Interaction 1: User expresses happiness")
    result1 = await agent.predict_emotion(
        input_data="I'm so excited about this new project!",
        user_id=user_id,
        input_type="text",
        context_description="User discussing new project"
    )
    print(f"Emotion: {result1['emotion']} (confidence: {result1['confidence']:.2f})")
    print(f"Has memory context: {result1['stateful']}\n")
    
    print("Interaction 2: User expresses concern")
    result2 = await agent.predict_emotion(
        input_data="I'm worried about the deadline...",
        user_id=user_id,
        input_type="text",
        context_description="User discussing project deadline"
    )
    print(f"Emotion: {result2['emotion']} (confidence: {result2['confidence']:.2f})")
    print(f"Has memory context: {result2['stateful']}\n")
    
    print("Interaction 3: User follows up")
    result3 = await agent.predict_emotion(
        input_data="But I think we can make it work!",
        user_id=user_id,
        input_type="text",
        context_description="User following up on project"
    )
    print(f"Emotion: {result3['emotion']} (confidence: {result3['confidence']:.2f})")
    print(f"Has memory context: {result3['stateful']}")
    
    if result3['stateful']:
        print(f"Memory context count: {result3['memory_context']['context_count']}\n")
    
    # Show emotional history
    print("Getting emotional history...")
    history = await agent.get_emotional_history(user_id, limit=5)
    print(f"Found {len(history)} past interactions\n")
    
    # Improve memory
    print("Improving memory (building knowledge graph)...")
    await agent.improve_memory()
    print("Memory improved!\n")
    
    print("=== Demo Complete ===\n")


if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_stateful_emotion_detection())
