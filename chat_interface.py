"""
Conversational Chat Interface with Cognee Memory

A chat interface that demonstrates context retention across conversations.
Shows the difference between stateless and stateful emotion AI.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from memory_emotion_agent import MemoryAwareEmotionAgent, create_memory_agent

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


class EmotionalChatSession:
    """
    A chat session that maintains emotional context.
    
    This demonstrates how Cognee memory enables true conversational AI
    that remembers past interactions and emotional patterns.
    """
    
    def __init__(
        self,
        user_id: str,
        agent: MemoryAwareEmotionAgent,
        session_id: Optional[str] = None
    ):
        """Initialize chat session.
        
        Args:
            user_id: User identifier
            agent: Memory-aware emotion agent
            session_id: Optional session identifier
        """
        self.user_id = user_id
        self.agent = agent
        self.session_id = session_id or str(uuid.uuid4())
        self.conversation_history: List[Dict[str, Any]] = []
        self.start_time = datetime.utcnow()
        
        LOGGER.info(f"Started chat session {self.session_id} for user {user_id}")
    
    async def send_message(
        self,
        message: str,
        show_comparison: bool = False
    ) -> Dict[str, Any]:
        """
        Send a message and get emotional response with context.
        
        Args:
            message: User message
            show_comparison: Whether to show stateless vs stateful comparison
        
        Returns:
            Response dictionary with emotion analysis and context
        """
        try:
            # Build context from conversation
            context_description = f"Chat message: {message}"
            if len(self.conversation_history) > 0:
                context_description += f" (conversation turn {len(self.conversation_history) + 1})"
            
            if show_comparison:
                # Show stateless vs stateful comparison
                result = await self.agent.compare_stateless_vs_stateful(
                    input_data=message,
                    user_id=self.user_id,
                    input_type="text",
                    context_description=context_description
                )
            else:
                # Regular stateful prediction
                result = await self.agent.predict_emotion(
                    input_data=message,
                    user_id=self.user_id,
                    input_type="text",
                    session_id=self.session_id,
                    context_description=context_description,
                    return_memory_context=True
                )
            
            # Add to conversation history
            turn = {
                "timestamp": datetime.utcnow().isoformat(),
                "message": message,
                "result": result,
                "turn_number": len(self.conversation_history) + 1
            }
            self.conversation_history.append(turn)
            
            return result
            
        except Exception as e:
            LOGGER.error(f"Error processing message: {e}")
            return {
                "error": str(e),
                "emotion": "error",
                "confidence": 0.0
            }
    
    async def get_emotional_summary(self) -> Dict[str, Any]:
        """Get emotional summary of the entire session."""
        try:
            patterns = await self.agent.get_emotional_patterns(
                user_id=self.user_id,
                time_window="current_session"
            )
            
            summary = {
                "session_id": self.session_id,
                "user_id": self.user_id,
                "start_time": self.start_time.isoformat(),
                "duration_minutes": (datetime.utcnow() - self.start_time).total_seconds() / 60,
                "turn_count": len(self.conversation_history),
                "patterns": patterns
            }
            
            return summary
            
        except Exception as e:
            LOGGER.error(f"Error getting emotional summary: {e}")
            return {"error": str(e)}
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the full conversation history."""
        return self.conversation_history


class ConversationalInterface:
    """
    Main conversational interface for EmoMemory.
    
    Handles multiple users and sessions, demonstrating the power
    of Cognee's memory across conversations.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        use_cloud: bool = False
    ):
        """Initialize conversational interface.
        
        Args:
            api_key: Cognee Cloud API key
            use_cloud: Whether to use Cognee Cloud
        """
        self.api_key = api_key
        self.use_cloud = use_cloud
        self.agent: Optional[MemoryAwareEmotionAgent] = None
        self.active_sessions: Dict[str, EmotionalChatSession] = {}
        
        LOGGER.info("Initialized conversational interface")
    
    async def initialize(self):
        """Initialize the emotion agent."""
        if self.agent is None:
            self.agent = await create_memory_agent(
                agent_type="multimodal",
                api_key=self.api_key,
                use_cloud=self.use_cloud
            )
            LOGGER.info("Emotion agent initialized")
    
    async def start_session(self, user_id: str) -> str:
        """
        Start a new chat session for a user.
        
        Args:
            user_id: User identifier
        
        Returns:
            Session ID
        """
        await self.initialize()
        
        session = EmotionalChatSession(
            user_id=user_id,
            agent=self.agent
        )
        
        self.active_sessions[session.session_id] = session
        
        LOGGER.info(f"Started session {session.session_id} for user {user_id}")
        return session.session_id
    
    async def chat(
        self,
        session_id: str,
        message: str,
        show_comparison: bool = False
    ) -> Dict[str, Any]:
        """
        Send a chat message in a session.
        
        Args:
            session_id: Session identifier
            message: User message
            show_comparison: Show stateless vs stateful comparison
        
        Returns:
            Response with emotion analysis
        """
        if session_id not in self.active_sessions:
            return {
                "error": "Session not found",
                "session_id": session_id
            }
        
        session = self.active_sessions[session_id]
        result = await session.send_message(message, show_comparison=show_comparison)
        
        return result
    
    async def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of a session."""
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        session = self.active_sessions[session_id]
        return await session.get_emotional_summary()
    
    async def get_user_history(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get emotional history for a user across all sessions."""
        await self.initialize()
        history = await self.agent.get_emotional_history(user_id, limit=limit)
        return history
    
    async def improve_memory(self) -> bool:
        """Run memory improvement (cognify)."""
        await self.initialize()
        return await self.agent.improve_memory()
    
    async def forget_user(self, user_id: str) -> bool:
        """Forget all data for a user (GDPR compliance)."""
        await self.initialize()
        return await self.agent.forget_user_data(user_id)


async def demo_conversation():
    """
    Demo: A conversation that shows memory in action.
    
    This demonstrates the key value proposition:
    - Without memory: Each message is independent
    - With memory: Context flows across the conversation
    """
    print("\n" + "="*60)
    print("  EmoMemory: Conversational AI That Never Forgets")
    print("  Powered by Cognee Memory")
    print("="*60 + "\n")
    
    # Initialize interface
    interface = ConversationalInterface(use_cloud=False)
    
    # Start session
    user_id = "demo_user"
    session_id = await interface.start_session(user_id)
    print(f"Started session: {session_id}\n")
    
    # Simulate a conversation
    conversation = [
        ("Hi! I just started a new job today!", "User introduces themselves"),
        ("I'm a bit nervous about meeting my new team...", "User expresses concern"),
        ("But my manager seems really nice!", "User shares positive experience"),
        ("I'm worried I won't be good enough though.", "User expresses self-doubt"),
        ("My friends keep telling me I'll do great.", "User mentions support system"),
    ]
    
    print("CONVERSATION WITH MEMORY:\n")
    print("-" * 60)
    
    for i, (message, description) in enumerate(conversation, 1):
        print(f"\nTurn {i}: {description}")
        print(f"User: {message}")
        
        result = await interface.chat(session_id, message)
        
        emotion = result.get("emotion", "unknown")
        confidence = result.get("confidence", 0.0)
        has_context = result.get("stateful", False)
        
        print(f"→ Detected Emotion: {emotion.upper()} (confidence: {confidence:.2%})")
        print(f"→ Has Memory Context: {'YES' if has_context else 'NO'}")
        
        if has_context and result.get("memory_context"):
            context_count = result["memory_context"].get("context_count", 0)
            if context_count > 0:
                print(f"→ Using {context_count} past interaction(s) as context")
        
        await asyncio.sleep(0.5)  # Small delay for readability
    
    print("\n" + "-" * 60)
    
    # Show session summary
    print("\nSESSION SUMMARY:\n")
    summary = await interface.get_session_summary(session_id)
    print(f"Session ID: {summary.get('session_id', 'N/A')}")
    print(f"Total turns: {summary.get('turn_count', 0)}")
    print(f"Duration: {summary.get('duration_minutes', 0):.2f} minutes")
    
    # Show user history
    print("\nUSER EMOTIONAL HISTORY:\n")
    history = await interface.get_user_history(user_id, limit=5)
    print(f"Total interactions stored: {len(history)}")
    
    # Improve memory
    print("\nIMPROVING MEMORY (Building Knowledge Graph)...")
    await interface.improve_memory()
    print("✓ Memory improved! Cognee has built connections between interactions.\n")
    
    # Demo comparison
    print("\n" + "="*60)
    print("  COMPARISON: Stateless vs Stateful")
    print("="*60 + "\n")
    
    test_message = "I'm feeling better about the job now!"
    print(f"Test Message: \"{test_message}\"\n")
    
    result = await interface.chat(session_id, test_message, show_comparison=True)
    
    if "stateless" in result and "stateful" in result:
        print("WITHOUT MEMORY (Stateless):")
        print(f"  Emotion: {result['stateless']['emotion']}")
        print(f"  Confidence: {result['stateless']['confidence']:.2%}")
        print(f"  Context: None\n")
        
        print("WITH MEMORY (Stateful):")
        print(f"  Emotion: {result['stateful']['emotion']}")
        print(f"  Confidence: {result['stateful']['confidence']:.2%}")
        print(f"  Context: {'YES - Using past interactions' if result['stateful']['has_context'] else 'None'}")
        
        if result.get("difference", {}).get("memory_enhanced"):
            print(f"\n✨ Memory Enhanced: YES")
            print(f"   Confidence Delta: {result['difference']['confidence_delta']:+.2%}")
    
    print("\n" + "="*60)
    print("  Demo Complete!")
    print("="*60 + "\n")


async def interactive_chat():
    """Interactive chat mode for testing."""
    print("\n" + "="*60)
    print("  EmoMemory: Interactive Chat")
    print("  Type 'quit' to exit, 'history' to see past interactions")
    print("  Type 'summary' to see session summary")
    print("="*60 + "\n")
    
    interface = ConversationalInterface(use_cloud=False)
    
    user_id = input("Enter your user ID (or press Enter for 'demo_user'): ").strip()
    if not user_id:
        user_id = "demo_user"
    
    session_id = await interface.start_session(user_id)
    print(f"\nStarted session: {session_id}")
    print("Ready to chat! Your emotions and context are being remembered.\n")
    
    while True:
        try:
            message = input("You: ").strip()
            
            if not message:
                continue
            
            if message.lower() == "quit":
                print("\nEnding session...")
                summary = await interface.get_session_summary(session_id)
                print(f"Total turns: {summary.get('turn_count', 0)}")
                break
            
            if message.lower() == "history":
                history = await interface.get_user_history(user_id, limit=10)
                print(f"\nFound {len(history)} past interactions")
                continue
            
            if message.lower() == "summary":
                summary = await interface.get_session_summary(session_id)
                print(f"\nSession Summary:")
                print(f"  Turns: {summary.get('turn_count', 0)}")
                print(f"  Duration: {summary.get('duration_minutes', 0):.2f} minutes")
                continue
            
            # Process message
            result = await interface.chat(session_id, message)
            
            emotion = result.get("emotion", "unknown")
            confidence = result.get("confidence", 0.0)
            has_context = result.get("stateful", False)
            
            print(f"EmoMemory: I detect {emotion.upper()} emotion (confidence: {confidence:.2%})")
            
            if has_context:
                print(f"           [Using context from {result.get('memory_context', {}).get('context_count', 0)} past interaction(s)]")
            else:
                print(f"           [No prior context for you yet]")
            
            print()
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")
            break


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        asyncio.run(interactive_chat())
    else:
        asyncio.run(demo_conversation())
