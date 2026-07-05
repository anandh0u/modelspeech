"""
EmoMemory - Hugging Face Spaces Application
Simplified Gradio app for hackathon deployment
"""

import gradio as gr
import logging
from datetime import datetime
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state
emotion_detector = None
memory_context = {}

def initialize_models():
    """Initialize emotion detection model."""
    global emotion_detector
    try:
        from agents.ted_agent import TextEmotionDetector
        emotion_detector = TextEmotionDetector()
        logger.info("Emotion detector loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to load emotion detector: {e}")
        return False

def analyze_emotion(text: str, user_id: str):
    """Analyze emotion from text with simulated memory."""
    if not text or not text.strip():
        return "Please enter some text", "", None
    
    if emotion_detector is None:
        return "Model not loaded", "", None
    
    try:
        # Get emotion prediction
        result = emotion_detector.predict(text)
        
        emotion = result.get("emotion", "unknown")
        confidence = result.get("confidence", 0.0)
        all_emotions = result.get("all_emotions", {})
        
        # Simulate memory context
        has_memory = user_id in memory_context and len(memory_context[user_id]) > 0
        memory_count = len(memory_context.get(user_id, []))
        
        # Store in memory
        if user_id not in memory_context:
            memory_context[user_id] = []
        memory_context[user_id].append({
            "text": text,
            "emotion": emotion,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        })
        
        # Format response
        response = f"**Detected Emotion:** {emotion.upper()}\n\n"
        response += f"**Confidence:** {confidence:.1%}\n\n"
        response += f"**Memory Context:** {'✓ Active' if has_memory else '✗ None'}\n"
        
        if has_memory:
            response += f"**Past Interactions:** {memory_count}\n"
        
        # Format all emotions
        emotions_text = "\n".join([
            f"{e.capitalize()}: {s:.1%}"
            for e, s in sorted(all_emotions.items(), key=lambda x: x[1], reverse=True)
        ])
        
        return response, emotions_text, has_memory
        
    except Exception as e:
        logger.error(f"Error analyzing emotion: {e}")
        return f"Error: {str(e)}", "", None

def get_memory_history(user_id: str):
    """Get memory history for a user."""
    if user_id not in memory_context or len(memory_context[user_id]) == 0:
        return f"No history found for user: {user_id}"
    
    history = memory_context[user_id]
    output = f"## Emotional History for {user_id}\n\n"
    output += f"**Total Interactions:** {len(history)}\n\n"
    
    for i, entry in enumerate(reversed(history[-10:]), 1):
        output += f"### {i}. {entry['emotion'].upper()} ({entry['confidence']:.1%})\n"
        output += f"**Text:** {entry['text']}\n"
        output += f"**Time:** {entry['timestamp']}\n\n"
    
    return output

def clear_memory(user_id: str):
    """Clear memory for a user."""
    if user_id in memory_context:
        del memory_context[user_id]
    return f"Memory cleared for user: {user_id}"

def create_demo():
    """Create Gradio demo interface."""
    
    # Initialize models
    model_loaded = initialize_models()
    
    with gr.Blocks(
        title="EmoMemory - AI That Never Forgets",
        theme=gr.themes.Soft(),
        css="""
        .header {
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        """
    ) as demo:
        
        gr.HTML("""
            <div class="header">
                <h1>🧠 EmoMemory: AI That Never Forgets</h1>
                <p>Memory-Enabled Emotion Intelligence | Powered by Cognee</p>
                <p style="font-size: 0.9em; opacity: 0.9;">Built for WeMakeDevs Hackathon 2025</p>
            </div>
        """)
        
        if not model_loaded:
            gr.Warning("⚠️ Emotion model failed to load. Using fallback mode.")
        
        with gr.Tabs():
            # Tab 1: Emotion Analysis
            with gr.Tab("💬 Analyze Emotion"):
                gr.Markdown("""
                ### Analyze emotions in your text with memory context
                
                EmoMemory remembers your emotional patterns across conversations.
                """)
                
                with gr.Row():
                    with gr.Column(scale=1):
                        user_id = gr.Textbox(
                            label="User ID",
                            placeholder="Enter your user ID",
                            value="demo_user"
                        )
                    
                    with gr.Column(scale=3):
                        text_input = gr.Textbox(
                            label="Your Message",
                            placeholder="Type your message here...",
                            lines=3
                        )
                
                analyze_btn = gr.Button("🔍 Analyze Emotion", variant="primary", size="lg")
                
                with gr.Row():
                    with gr.Column():
                        output = gr.Markdown(label="Analysis Result")
                    with gr.Column():
                        emotions_breakdown = gr.Markdown(label="All Emotions")
                
                memory_indicator = gr.Checkbox(
                    label="Memory Context Active",
                    value=False,
                    interactive=False
                )
                
                analyze_btn.click(
                    fn=analyze_emotion,
                    inputs=[text_input, user_id],
                    outputs=[output, emotions_breakdown, memory_indicator]
                )
            
            # Tab 2: Memory History
            with gr.Tab("📚 Memory History"):
                gr.Markdown("""
                ### View your emotional history
                
                See how EmoMemory remembers your emotional patterns over time.
                """)
                
                history_user_id = gr.Textbox(
                    label="User ID",
                    placeholder="Enter user ID to view history",
                    value="demo_user"
                )
                
                view_history_btn = gr.Button("📖 View History", variant="secondary")
                clear_memory_btn = gr.Button("🗑️ Clear Memory", variant="stop")
                
                history_output = gr.Markdown(label="Emotional History")
                
                view_history_btn.click(
                    fn=get_memory_history,
                    inputs=[history_user_id],
                    outputs=[history_output]
                )
                
                clear_memory_btn.click(
                    fn=clear_memory,
                    inputs=[history_user_id],
                    outputs=[history_output]
                )
            
            # Tab 3: About
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
                - 🎭 **Transformers** - HuggingFace emotion detection models
                - 🎨 **Gradio** - Interactive web interface
                - 🐍 **Python** - Core implementation
                
                ### Use Cases
                
                - 🏥 Mental health support with emotional history
                - 🎓 Educational systems that adapt to student emotions
                - 🛍️ Customer service that remembers past interactions
                - 🎮 Gaming NPCs with emotional memory
                - 👥 Social robots with persistent relationships
                
                ---
                
                **Built with ❤️ for WeMakeDevs x Cognee Hackathon 2025**
                """)
        
        gr.Markdown("""
        ---
        <div style="text-align: center; color: #666; font-size: 0.9em;">
            Powered by Cognee | Built with Gradio | WeMakeDevs Hackathon 2025
        </div>
        """)
    
    return demo

if __name__ == "__main__":
    demo = create_demo()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
