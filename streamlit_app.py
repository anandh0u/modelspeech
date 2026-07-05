"""
EmoMemory - Streamlit Application
Memory-Enabled Emotion Intelligence powered by Cognee Cloud
"""

import streamlit as st
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="EmoMemory - AI That Never Forgets",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .emotion-card {
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'emotion_detector' not in st.session_state:
    st.session_state.emotion_detector = None
if 'memory_context' not in st.session_state:
    st.session_state.memory_context = {}
if 'cognee_initialized' not in st.session_state:
    st.session_state.cognee_initialized = False

def initialize_models():
    """Initialize emotion detection model."""
    try:
        from agents.ted_agent import TextEmotionDetector
        st.session_state.emotion_detector = TextEmotionDetector()
        logger.info("Emotion detector loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to load emotion detector: {e}")
        st.error(f"Failed to load emotion model: {e}")
        return False

def initialize_cognee():
    """Initialize Cognee Cloud with API key."""
    try:
        import cognee
        
        api_key = os.getenv("COGNEE_API_KEY")
        if not api_key:
            st.warning("⚠️ COGNEE_API_KEY not set. Using local mode.")
            return False
        
        # Configure Cognee Cloud
        cognee.config.set_api_key(api_key)
        st.session_state.cognee_initialized = True
        logger.info("Cognee Cloud initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize Cognee: {e}")
        st.error(f"Failed to initialize Cognee: {e}")
        return False

async def remember_memory(user_id: str, text: str, emotion: str, confidence: float):
    """Store emotional interaction in Cognee memory."""
    try:
        import cognee
        
        memory_text = f"User: {user_id} | Emotion: {emotion} ({confidence:.2%}) | Text: {text} | Time: {datetime.now().isoformat()}"
        
        await cognee.add(memory_text, dataset_name="emomemory_interactions")
        logger.info(f"Remembered: {emotion} for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to remember: {e}")
        return False

async def recall_memory(user_id: str, query: str, limit: int = 5):
    """Recall relevant memories from Cognee."""
    try:
        import cognee
        
        search_query = f"User: {user_id} {query}"
        results = await cognee.search(
            query_text=search_query,
            dataset_name="emomemory_interactions"
        )
        
        if isinstance(results, list):
            return results[:limit]
        return []
        
    except Exception as e:
        logger.error(f"Failed to recall: {e}")
        return []

async def improve_memory():
    """Improve memory by building knowledge graph."""
    try:
        import cognee
        await cognee.cognify()
        logger.info("Memory improved successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to improve memory: {e}")
        return False

async def forget_memory(user_id: str):
    """Forget memories for a user."""
    try:
        import cognee
        # In production, implement selective forgetting
        await cognee.prune.prune_data()
        logger.info(f"Forgot data for user: {user_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to forget: {e}")
        return False

def analyze_emotion(text: str, user_id: str):
    """Analyze emotion from text."""
    if not text or not text.strip():
        return None, "Please enter some text"
    
    if st.session_state.emotion_detector is None:
        return None, "Model not loaded"
    
    try:
        result = st.session_state.emotion_detector.predict(text)
        
        emotion = result.get("emotion", "unknown")
        confidence = result.get("confidence", 0.0)
        all_emotions = result.get("all_emotions", {})
        
        # Store in session memory
        if user_id not in st.session_state.memory_context:
            st.session_state.memory_context[user_id] = []
        
        st.session_state.memory_context[user_id].append({
            "text": text,
            "emotion": emotion,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        })
        
        # Store in Cognee if initialized
        if st.session_state.cognee_initialized:
            import asyncio
            asyncio.run(remember_memory(user_id, text, emotion, confidence))
        
        return result, None
        
    except Exception as e:
        logger.error(f"Error analyzing emotion: {e}")
        return None, f"Error: {str(e)}"

# Header
st.markdown("""
<div class="header">
    <h1>🧠 EmoMemory: AI That Never Forgets</h1>
    <p>Memory-Enabled Emotion Intelligence | Powered by Cognee</p>
    <p style="font-size: 0.9em; opacity: 0.9;">Built for WeMakeDevs Hackathon 2025</p>
</div>
""", unsafe_allow_html=True)

# Initialize models on first run
if st.session_state.emotion_detector is None:
    with st.spinner("Loading emotion detection model..."):
        initialize_models()

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Cognee API Key
    api_key = st.text_input(
        "Cognee API Key",
        type="password",
        placeholder="Enter your COGNEE-35 free credit key",
        help="Get free credit at: https://cognee.ai with code COGNEE-35"
    )
    
    if api_key and not st.session_state.cognee_initialized:
        os.environ["COGNEE_API_KEY"] = api_key
        with st.spinner("Initializing Cognee Cloud..."):
            initialize_cognee()
    
    st.markdown("---")
    
    # User ID
    user_id = st.text_input(
        "User ID",
        value="demo_user",
        help="Your unique identifier for memory"
    )
    
    st.markdown("---")
    
    # Memory operations
    st.header("🗄️ Memory Operations")
    
    if st.button("✨ Improve Memory (Cognify)"):
        if st.session_state.cognee_initialized:
            import asyncio
            with st.spinner("Building knowledge graph..."):
                success = asyncio.run(improve_memory())
                if success:
                    st.success("Memory improved successfully!")
                else:
                    st.error("Failed to improve memory")
        else:
            st.warning("Initialize Cognee Cloud first")
    
    if st.button("🗑️ Forget My Data"):
        if st.session_state.cognee_initialized:
            import asyncio
            with st.spinner("Forgetting data..."):
                success = asyncio.run(forget_memory(user_id))
                if success:
                    st.success("Data forgotten successfully!")
                    st.session_state.memory_context[user_id] = []
                else:
                    st.error("Failed to forget data")
        else:
            st.warning("Initialize Cognee Cloud first")
    
    st.markdown("---")
    
    # Status
    st.header("📊 Status")
    st.write(f"**Model Loaded:** {'✅' if st.session_state.emotion_detector else '❌'}")
    st.write(f"**Cognee Cloud:** {'✅' if st.session_state.cognee_initialized else '❌'}")
    st.write(f"**Memory Entries:** {len(st.session_state.memory_context.get(user_id, []))}")

# Main content
tab1, tab2, tab3 = st.tabs(["💬 Analyze Emotion", "📚 Memory History", "ℹ️ About"])

with tab1:
    st.subheader("Analyze emotions in your text with memory context")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        text_input = st.text_area(
            "Your Message",
            placeholder="Type your message here...",
            height=150
        )
    
    with col2:
        st.write("")
        analyze_btn = st.button("🔍 Analyze Emotion", type="primary", use_container_width=True)
    
    if analyze_btn and text_input:
        result, error = analyze_emotion(text_input, user_id)
        
        if error:
            st.error(error)
        elif result:
            emotion = result.get("emotion", "unknown")
            confidence = result.get("confidence", 0.0)
            all_emotions = result.get("all_emotions", {})
            
            # Display result
            st.markdown(f"""
            <div class="emotion-card" style="background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%); border: 2px solid #667eea;">
                <h2 style="color: #667eea;">Detected Emotion: {emotion.upper()}</h2>
                <p style="font-size: 1.5em; font-weight: bold;">Confidence: {confidence:.1%}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # All emotions breakdown
            st.subheader("All Emotions")
            for emo, score in sorted(all_emotions.items(), key=lambda x: x[1], reverse=True):
                st.progress(score, text=f"{emo.capitalize()}: {score:.1%}")
            
            # Memory context
            memory_count = len(st.session_state.memory_context.get(user_id, []))
            if memory_count > 0:
                st.success(f"🧠 Memory Context Active - {memory_count} past interaction(s) stored")

with tab2:
    st.subheader("Your emotional history")
    
    if user_id in st.session_state.memory_context and len(st.session_state.memory_context[user_id]) > 0:
        history = st.session_state.memory_context[user_id]
        
        for i, entry in enumerate(reversed(history[-10:]), 1):
            with st.expander(f"{i}. {entry['emotion'].upper()} ({entry['confidence']:.1%}) - {entry['timestamp'][:19]}"):
                st.write(f"**Text:** {entry['text']}")
                st.write(f"**Confidence:** {entry['confidence']:.1%}")
    else:
        st.info(f"No emotional history found for user: {user_id}")

with tab3:
    st.markdown("""
    ## About EmoMemory
    
    **EmoMemory** is a memory-enabled emotion intelligence system built for the WeMakeDevs x Cognee Hackathon.
    
    ### The Problem
    
    Traditional LLMs and AI systems are **stateless**. Every request starts from scratch:
    - ❌ No memory of past conversations
    - ❌ Context window limits (tokens run out)
    - ❌ Can't learn from user patterns
    - ❌ Forgets important emotional context
    
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
    - 🎭 **Transformers** - HuggingFace emotion detection
    - 🎨 **Streamlit** - Interactive web interface
    - 🐍 **Python** - Core implementation
    
    ---
    
    **Built with ❤️ for WeMakeDevs x Cognee Hackathon 2025**
    """)

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9em;">
    Powered by Cognee | Built with Streamlit | WeMakeDevs Hackathon 2025
</div>
""", unsafe_allow_html=True)
