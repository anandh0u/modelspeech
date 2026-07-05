# Hugging Face Spaces version of web_demo.py
# This is identical to web_demo.py but named app.py for HF Spaces

import gradio as gr
import asyncio
import logging
from typing import Optional, List, Tuple
from datetime import datetime
import uuid

# Import from our modules
from memory_emotion_agent import create_memory_agent

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

# Global emotion agent (initialized on startup)
emotion_agent = None


async def initialize_agent():
    """Initialize the emotion agent."""
    global emotion_agent
    if emotion_agent is None:
        emotion_agent = await create_memory_agent(
            agent_type="multimodal",
            use_cloud=False  # Use local for demo
        )
    return emotion_agent


def send_chat_message_sync(message: str, chat_history: List, session_id: Optional[str]) -> Tuple[List, str, str]:
    """Synchronous wrapper for chat."""
    return asyncio.run(send_chat_message(message, chat_history, session_id))


async def send_chat_message(message: str, chat_history: List, session_id: Optional[str]) -> Tuple[List, str, str]:
    """Send chat message with emotion detection."""
    global emotion_agent
    
    if not message:
        return chat_history, "", session_id or str(uuid.uuid4())
    
    # Initialize agent if needed
    if emotion_agent is None:
        await initialize_agent()
    
    # Generate session ID if needed
    if not session_id:
        session_id = str(uuid.uuid4())
    
    try:
        # Make prediction
        result = await emotion_agent.predict_emotion(
            input_data=message,
            user_id="demo_user",
            input_type="text",
            session_id=session_id,
            context_description=message,
            return_memory_context=True
        )
        
        # Format response
        emotion = result.get("emotion", "unknown")
        confidence = result.get("confidence", 0.0)
        has_context = result.get("stateful", False)
        
        response = f"**Emotion:** {emotion.upper()} ({confidence:.1%} confidence)\n\n"
        
        if has_context:
            memory_count = result.get("memory_context", {}).get("context_count", 0)
            response += f"🧠 **Memory Context:** Using {memory_count} past interaction(s)\n"
        else:
            response += "💭 **No Prior Context** (First interaction)\n"
        
        # Add to chat history
        chat_history.append((message, response))
        
        return chat_history, "", session_id
        
    except Exception as e:
        error_response = f"❌ Error: {str(e)}"
        chat_history.append((message, error_response))
        return chat_history, "", session_id


def create_demo():
    """Create Gradio demo."""
    
    with gr.Blocks(
        title="EmoMemory - AI That Never Forgets",
        theme=gr.themes.Soft(primary_hue="blue")
    ) as demo:
        
        gr.HTML("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; margin-bottom: 20px;">
            <h1>🧠 EmoMemory</h1>
            <p>Memory-Enabled Emotion AI | Powered by Cognee</p>
            <p><i>Built for WeMakeDevs Hackathon 2025</i></p>
        </div>
        """)
        
        # Session state
        session_id_state = gr.State(None)
        
        with gr.Row():
            with gr.Column(scale=3):
                gr.Markdown("## 💬 Chat with Memory")
                
                chatbot = gr.Chatbot(
                    label="Conversation",
                    height=400,
                    show_label=False
                )
                
                with gr.Row():
                    chat_input = gr.Textbox(
                        label="Your Message",
                        placeholder="Type your message here...",
                        lines=2,
                        scale=4
                    )
                    send_btn = gr.Button("Send", scale=1, variant="primary")
                
                gr.Examples(
                    examples=[
                        "I'm so excited about my new project!",
                        "I'm worried about the deadline...",
                        "Everything is going great today!",
                        "I'm frustrated with this situation.",
                    ],
                    inputs=chat_input
                )
            
            with gr.Column(scale=1):
                gr.Markdown("### 💡 How It Works")
                gr.Markdown("""
                **The Problem:**
                Traditional AI forgets everything after each interaction.
                
                **The Solution:**
                EmoMemory uses Cognee to remember your emotional context!
                
                **Try it:**
                1. Send your first message
                2. Send a follow-up message
                3. Watch the AI remember your context!
                
                **Memory Operations:**
                - ✅ REMEMBER - Store emotions
                - ✅ RECALL - Retrieve context
                - ✅ IMPROVE - Build patterns
                - ✅ FORGET - Remove data
                """)
                
                new_chat_btn = gr.Button("🆕 New Chat Session")
        
        gr.Markdown("---")
        
        gr.Markdown("""
        ## 🏆 About This Project
        
        **EmoMemory** demonstrates how Cognee solves the AI amnesia problem:
        - 🧠 **Persistent Memory** - AI that remembers across sessions
        - 🎯 **Context-Aware** - Uses past emotional states
        - 📊 **Pattern Learning** - Builds knowledge graphs
        - 🔒 **GDPR Compliant** - Forget on request
        
        ### Built With:
        - **Cognee** - Hybrid graph-vector memory
        - **Gradio** - Interactive interface
        - **Python** - Core implementation
        
        ### Hackathon: WeMakeDevs x Cognee 2025
        
        **GitHub:** [Your Repo Link]
        """)
        
        # Event handlers
        send_btn.click(
            fn=send_chat_message_sync,
            inputs=[chat_input, chatbot, session_id_state],
            outputs=[chatbot, chat_input, session_id_state]
        )
        
        chat_input.submit(
            fn=send_chat_message_sync,
            inputs=[chat_input, chatbot, session_id_state],
            outputs=[chatbot, chat_input, session_id_state]
        )
        
        new_chat_btn.click(
            fn=lambda: ([], None),
            outputs=[chatbot, session_id_state]
        )
    
    return demo


if __name__ == "__main__":
    demo = create_demo()
    demo.launch()
