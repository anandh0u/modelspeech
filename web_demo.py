"""
EmoMemory Web Demo

Interactive Gradio web application demonstrating Cognee-powered
memory-enabled emotion AI vs traditional stateless approaches.
"""

import asyncio
import gradio as gr
import logging
from typing import Optional, Tuple, List
from datetime import datetime
import json

from chat_interface import ConversationalInterface
from memory_emotion_agent import create_memory_agent

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

# Global interface instance
interface: Optional[ConversationalInterface] = None
current_sessions = {}


def initialize_interface(api_key: str = "", use_cloud: bool = False):
    """Initialize the conversational interface."""
    global interface
    if interface is None:
        interface = ConversationalInterface(
            api_key=api_key if api_key else None,
            use_cloud=use_cloud
        )
        LOGGER.info("Interface initialized")
    return interface


async def start_new_session(user_id: str) -> Tuple[str, str]:
    """Start a new chat session."""
    global interface, current_sessions
    
    if not user_id:
        return "❌ Please enter a User ID", ""
    
    initialize_interface()
    
    try:
        session_id = await interface.start_session(user_id)
        current_sessions[user_id] = session_id
        
        message = f"✅ Started new session for user: {user_id}\n"
        message += f"Session ID: {session_id}\n\n"
        message += "Your emotions and context will be remembered across conversations!"
        
        return message, session_id
        
    except Exception as e:
        LOGGER.error(f"Error starting session: {e}")
        return f"❌ Error: {str(e)}", ""


async def send_message_stateful(
    user_id: str,
    message: str,
    session_id: str,
    chat_history: List
) -> Tuple[List, str]:
    """Send message with stateful processing."""
    global interface
    
    if not message or not user_id:
        return chat_history, "Please enter both User ID and message"
    
    if not session_id:
        # Start new session
        session_id = await interface.start_session(user_id)
        current_sessions[user_id] = session_id
    
    try:
        result = await interface.chat(session_id, message, show_comparison=False)
        
        emotion = result.get("emotion", "unknown")
        confidence = result.get("confidence", 0.0)
        has_context = result.get("stateful", False)
        
        # Format response
        response = f"**Emotion:** {emotion.upper()}\n"
        response += f"**Confidence:** {confidence:.2%}\n"
        response += f"**Memory Context:** {'✓ YES' if has_context else '✗ NO'}\n"
        
        if has_context and result.get("memory_context"):
            context_count = result["memory_context"].get("context_count", 0)
            if context_count > 0:
                response += f"**Past Interactions Used:** {context_count}\n"
        
        # Add to chat history
        chat_history.append((message, response))
        
        status = f"✅ Processed with {'memory context' if has_context else 'no prior context'}"
        
        return chat_history, status
        
    except Exception as e:
        LOGGER.error(f"Error processing message: {e}")
        return chat_history, f"❌ Error: {str(e)}"


async def compare_stateless_stateful(
    user_id: str,
    message: str,
    session_id: str
) -> Tuple[str, str, str]:
    """Compare stateless vs stateful predictions."""
    global interface
    
    if not message or not user_id:
        return "Enter User ID and message", "", ""
    
    initialize_interface()
    
    if not session_id:
        session_id = await interface.start_session(user_id)
        current_sessions[user_id] = session_id
    
    try:
        result = await interface.chat(session_id, message, show_comparison=True)
        
        # Stateless result
        stateless_text = "## Without Memory (Stateless)\n\n"
        if "stateless" in result:
            stateless_text += f"**Emotion:** {result['stateless']['emotion'].upper()}\n"
            stateless_text += f"**Confidence:** {result['stateless']['confidence']:.2%}\n"
            stateless_text += f"**Context:** None\n\n"
            stateless_text += "ℹ️ This is like a typical LLM - no memory of past interactions."
        
        # Stateful result
        stateful_text = "## With Memory (Stateful)\n\n"
        if "stateful" in result:
            stateful_text += f"**Emotion:** {result['stateful']['emotion'].upper()}\n"
            stateful_text += f"**Confidence:** {result['stateful']['confidence']:.2%}\n"
            stateful_text += f"**Context:** {'YES' if result['stateful']['has_context'] else 'None'}\n\n"
            
            if result['stateful']['has_context']:
                context_count = result['stateful']['memory_context'].get('context_count', 0)
                stateful_text += f"✨ Using {context_count} past interaction(s) as context\n\n"
            
            stateful_text += "🧠 Powered by Cognee - remembers your emotional patterns!"
        
        # Difference
        diff_text = "## Key Differences\n\n"
        if "difference" in result:
            diff = result["difference"]
            
            if diff.get("emotion_changed"):
                diff_text += "🔄 **Emotion Detection Changed** due to memory context\n"
            else:
                diff_text += "✓ **Same Emotion** detected\n"
            
            confidence_delta = diff.get("confidence_delta", 0)
            if abs(confidence_delta) > 0.01:
                diff_text += f"📊 **Confidence Delta:** {confidence_delta:+.2%}\n"
            
            if diff.get("memory_enhanced"):
                diff_text += "\n✨ **Memory Enhancement:** Active\n"
                diff_text += "The stateful model used past emotional patterns to improve prediction."
        
        return stateless_text, stateful_text, diff_text
        
    except Exception as e:
        LOGGER.error(f"Error in comparison: {e}")
        error_msg = f"❌ Error: {str(e)}"
        return error_msg, error_msg, error_msg


async def get_user_history_display(user_id: str) -> str:
    """Get formatted user history."""
    global interface
    
    if not user_id:
        return "Enter a User ID"
    
    initialize_interface()
    
    try:
        history = await interface.get_user_history(user_id, limit=20)
        
        if not history:
            return f"No interaction history found for user: {user_id}"
        
        output = f"# Emotional History for {user_id}\n\n"
        output += f"**Total Interactions:** {len(history)}\n\n"
        output += "---\n\n"
        
        for i, entry in enumerate(history, 1):
            output += f"### Interaction {i}\n\n"
            # Note: The actual structure depends on what Cognee returns
            # This is a placeholder format
            output += f"```\n{json.dumps(entry, indent=2)}\n```\n\n"
        
        return output
        
    except Exception as e:
        LOGGER.error(f"Error getting history: {e}")
        return f"❌ Error: {str(e)}"


async def improve_memory_action() -> str:
    """Run memory improvement."""
    global interface
    
    initialize_interface()
    
    try:
        await interface.improve_memory()
        return "✅ Memory improved! Cognee has built knowledge graph connections between interactions."
    except Exception as e:
        LOGGER.error(f"Error improving memory: {e}")
        return f"❌ Error: {str(e)}"


async def forget_user_action(user_id: str) -> str:
    """Forget user data (GDPR compliance)."""
    global interface
    
    if not user_id:
        return "Enter a User ID to forget"
    
    initialize_interface()
    
    try:
        success = await interface.forget_user(user_id)
        if success:
            return f"✅ Forgot all data for user: {user_id}"
        else:
            return f"⚠️ Failed to forget data for user: {user_id}"
    except Exception as e:
        LOGGER.error(f"Error forgetting user: {e}")
        return f"❌ Error: {str(e)}"


# Wrapper functions for Gradio (synchronous)
def start_session_sync(user_id: str) -> Tuple[str, str]:
    """Sync wrapper for start_new_session."""
    return asyncio.run(start_new_session(user_id))


def send_message_sync(user_id: str, message: str, session_id: str, chat_history: List) -> Tuple[List, str]:
    """Sync wrapper for send_message_stateful."""
    return asyncio.run(send_message_stateful(user_id, message, session_id, chat_history))


def compare_sync(user_id: str, message: str, session_id: str) -> Tuple[str, str, str]:
    """Sync wrapper for compare_stateless_stateful."""
    return asyncio.run(compare_stateless_stateful(user_id, message, session_id))


def get_history_sync(user_id: str) -> str:
    """Sync wrapper for get_user_history_display."""
    return asyncio.run(get_user_history_display(user_id))


def improve_memory_sync() -> str:
    """Sync wrapper for improve_memory_action."""
    return asyncio.run(improve_memory_action())


def forget_user_sync(user_id: str) -> str:
    """Sync wrapper for forget_user_action."""
    return asyncio.run(forget_user_action(user_id))


def create_demo_app():
    """Create the Gradio demo application."""
    
    with gr.Blocks(
        title="EmoMemory - AI That Never Forgets",
        theme=gr.themes.Soft()
    ) as demo:
        
        gr.Markdown("""
        # 🧠 EmoMemory: Memory-Enabled Emotion AI
        
        ### Powered by Cognee | Built for WeMakeDevs Hackathon
        
        **The Problem:** Traditional LLMs are stateless. They forget everything after each interaction.
        
        **The Solution:** EmoMemory uses Cognee to give AI a permanent memory layer that:
        - ✅ **Remembers** past emotional interactions
        - ✅ **Recalls** relevant context when needed
        - ✅ **Learns** patterns over time (memify/improve)
        - ✅ **Forgets** when appropriate (GDPR compliant)
        
        ---
        """)
        
        # Tab 1: Side-by-Side Comparison
        with gr.Tab("🔄 Stateless vs Stateful Comparison"):
            gr.Markdown("""
            ### See the Difference!
            
            Compare how the same message is processed **with** and **without** memory.
            This demonstrates the core value of Cognee's memory layer.
            """)
            
            with gr.Row():
                with gr.Column():
                    comp_user_id = gr.Textbox(
                        label="User ID",
                        placeholder="Enter your user ID (e.g., user_001)",
                        value="demo_user"
                    )
                    comp_message = gr.Textbox(
                        label="Your Message",
                        placeholder="Type your message here...",
                        lines=3
                    )
                    comp_session_id = gr.Textbox(
                        label="Session ID (auto-generated)",
                        interactive=False
                    )
                    comp_btn = gr.Button("🔍 Compare Predictions", variant="primary")
            
            with gr.Row():
                stateless_output = gr.Markdown(label="Without Memory")
                stateful_output = gr.Markdown(label="With Memory")
            
            diff_output = gr.Markdown(label="Analysis")
            
            comp_btn.click(
                fn=compare_sync,
                inputs=[comp_user_id, comp_message, comp_session_id],
                outputs=[stateless_output, stateful_output, diff_output]
            )
        
        # Tab 2: Chat Interface
        with gr.Tab("💬 Memory-Enabled Chat"):
            gr.Markdown("""
            ### Have a Conversation
            
            Chat with EmoMemory and watch it remember your emotional context!
            Start a session, then send multiple messages to see how context builds.
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    chat_user_id = gr.Textbox(
                        label="User ID",
                        placeholder="Enter your user ID",
                        value="demo_user"
                    )
                    chat_session_id = gr.Textbox(
                        label="Session ID",
                        interactive=False
                    )
                    start_btn = gr.Button("🚀 Start New Session", variant="secondary")
                    session_status = gr.Textbox(
                        label="Status",
                        interactive=False,
                        lines=4
                    )
                
                with gr.Column(scale=2):
                    chatbot = gr.Chatbot(
                        label="Conversation",
                        height=400
                    )
                    chat_input = gr.Textbox(
                        label="Your Message",
                        placeholder="Type your message...",
                        lines=2
                    )
                    with gr.Row():
                        send_btn = gr.Button("📤 Send", variant="primary")
                        clear_btn = gr.Button("🗑️ Clear Chat")
                    
                    chat_status = gr.Textbox(label="Message Status", interactive=False)
            
            start_btn.click(
                fn=start_session_sync,
                inputs=[chat_user_id],
                outputs=[session_status, chat_session_id]
            )
            
            send_btn.click(
                fn=send_message_sync,
                inputs=[chat_user_id, chat_input, chat_session_id, chatbot],
                outputs=[chatbot, chat_status]
            )
            
            clear_btn.click(
                fn=lambda: ([], ""),
                outputs=[chatbot, chat_status]
            )
        
        # Tab 3: Memory Management
        with gr.Tab("🗄️ Memory Management"):
            gr.Markdown("""
            ### Explore the Four Memory Lifecycle Operations
            
            Cognee provides four core memory operations:
            1. **Remember** - Store new interactions (happens automatically)
            2. **Recall** - Retrieve past contexts (see history below)
            3. **Improve/Memify** - Build knowledge graph connections
            4. **Forget** - Remove data (GDPR compliance)
            """)
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 📚 User History (Recall)")
                    history_user_id = gr.Textbox(
                        label="User ID",
                        placeholder="Enter user ID to view history",
                        value="demo_user"
                    )
                    history_btn = gr.Button("📖 View History", variant="secondary")
                    history_output = gr.Markdown(label="Emotional History")
                
                with gr.Column():
                    gr.Markdown("### 🧠 Memory Operations")
                    
                    improve_btn = gr.Button("✨ Improve Memory (Cognify)", variant="primary")
                    improve_output = gr.Textbox(label="Status", interactive=False)
                    
                    gr.Markdown("---")
                    
                    forget_user_id = gr.Textbox(
                        label="User ID to Forget",
                        placeholder="Enter user ID"
                    )
                    forget_btn = gr.Button("🗑️ Forget User (GDPR)", variant="stop")
                    forget_output = gr.Textbox(label="Status", interactive=False)
            
            history_btn.click(
                fn=get_history_sync,
                inputs=[history_user_id],
                outputs=[history_output]
            )
            
            improve_btn.click(
                fn=improve_memory_sync,
                outputs=[improve_output]
            )
            
            forget_btn.click(
                fn=forget_user_sync,
                inputs=[forget_user_id],
                outputs=[forget_output]
            )
        
        # Tab 4: About
        with gr.Tab("ℹ️ About"):
            gr.Markdown("""
            ## About EmoMemory
            
            **EmoMemory** is a memory-enabled emotion intelligence system built for the WeMakeDevs x Cognee Hackathon.
            
            ### The Problem
            
            Traditional LLMs and AI systems are **stateless**. Every request starts from scratch:
            - ❌ No memory of past conversations
            - ❌ Context window limits (tokens run out)
            - ❌ Can't learn from user patterns
            - ❌ Forgets important emotional context
            
            This is like having a therapist with amnesia - not very helpful!
            
            ### The Solution: Cognee Memory
            
            **Cognee** provides a hybrid graph-vector memory layer that enables:
            
            #### 1️⃣ Remember
            Store emotional interactions persistently in a knowledge graph
            
            #### 2️⃣ Recall
            Retrieve relevant past contexts using semantic search
            
            #### 3️⃣ Improve (Memify/Cognify)
            Build connections and patterns between memories
            
            #### 4️⃣ Forget
            Remove data when needed (GDPR compliant)
            
            ### Technology Stack
            
            - 🧠 **Cognee** - Memory layer and knowledge graph
            - 🎭 **Multimodal Emotion AI** - Text, speech, facial, video emotion detection
            - 🎨 **Gradio** - Interactive web interface
            - 🐍 **Python** - Core implementation
            
            ### Use Cases
            
            - 🏥 Mental health support with emotional history
            - 🎓 Educational systems that adapt to student emotions
            - 🛍️ Customer service that remembers past interactions
            - 🎮 Gaming NPCs with emotional memory
            - 👥 Social robots with persistent relationships
            
            ### Built With ❤️ by
            
            Your team name here! Built for WeMakeDevs Hackathon.
            
            ### Links
            
            - 📦 Cognee: [github.com/topoteretes/cognee](https://github.com/topoteretes/cognee)
            - 🎯 Hackathon: WeMakeDevs x Cognee Challenge
            - 🚀 Tracks: Cognee Cloud & Open Source
            
            ---
            
            **Note:** This demo uses mock emotion detection models. In production, replace with actual
            trained models for facial emotion detection (FED), speech emotion recognition (SER), 
            text emotion detection (TED), and audio emotion detection (AED).
            """)
    
    return demo


def main():
    """Launch the web demo."""
    demo = create_demo_app()
    
    # Launch with sharing enabled for easy demo
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,  # Set to True to get a public URL
        show_error=True
    )


if __name__ == "__main__":
    main()
