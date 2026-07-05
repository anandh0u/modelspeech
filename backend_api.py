"""
FastAPI Backend for EmoMemory
Simple backend for emotion detection with Cognee memory
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import asyncio
import logging
from datetime import datetime

# Import our modules
from memory_emotion_agent import create_memory_agent
from cognee_integration import CogneeMemoryManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="EmoMemory API",
    description="Memory-Enabled Emotion Intelligence powered by Cognee",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
agent = None

# Pydantic models
class EmotionRequest(BaseModel):
    text: str
    user_id: str
    session_id: Optional[str] = None
    context: Optional[str] = ""

class EmotionResponse(BaseModel):
    emotion: str
    confidence: float
    timestamp: str
    stateful: bool
    memory_context: Optional[Dict[str, Any]] = None
    all_emotions: Optional[Dict[str, float]] = None

class HistoryRequest(BaseModel):
    user_id: str
    limit: int = 10

class ComparisonRequest(BaseModel):
    text: str
    user_id: str
    context: Optional[str] = ""

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the emotion agent on startup."""
    global agent
    logger.info("Starting EmoMemory backend...")
    try:
        # Create agent with text-only mode for simplicity
        agent = await create_memory_agent(
            agent_type="ted",  # Text emotion detection only
            use_cloud=False  # Use local Cognee
        )
        logger.info("EmoMemory agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        # Continue without agent for graceful degradation
        agent = None

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "agent_loaded": agent is not None,
        "timestamp": datetime.utcnow().isoformat()
    }

# Predict emotion
@app.post("/predict", response_model=EmotionResponse)
async def predict_emotion(request: EmotionRequest):
    """Predict emotion from text with memory context."""
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        result = await agent.predict_emotion(
            input_data=request.text,
            user_id=request.user_id,
            input_type="text",
            session_id=request.session_id,
            context_description=request.context or request.text,
            return_memory_context=True
        )
        
        return EmotionResponse(
            emotion=result["emotion"],
            confidence=result["confidence"],
            timestamp=result.get("timestamp", datetime.utcnow().isoformat()),
            stateful=result["stateful"],
            memory_context=result.get("memory_context"),
            all_emotions=result.get("all_emotions")
        )
    except Exception as e:
        logger.error(f"Error predicting emotion: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Compare stateless vs stateful
@app.post("/compare")
async def compare_predictions(request: ComparisonRequest):
    """Compare stateless vs stateful predictions."""
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        result = await agent.compare_stateless_vs_stateful(
            input_data=request.text,
            user_id=request.user_id,
            input_type="text",
            context_description=request.context or request.text
        )
        return result
    except Exception as e:
        logger.error(f"Error in comparison: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get emotional history
@app.post("/history")
async def get_history(request: HistoryRequest):
    """Get emotional history for a user."""
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        history = await agent.get_emotional_history(
            user_id=request.user_id,
            limit=request.limit
        )
        return {"user_id": request.user_id, "history": history}
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Improve memory
@app.post("/improve")
async def improve_memory():
    """Run memory improvement (cognify)."""
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        success = await agent.improve_memory()
        return {"success": success, "message": "Memory improved" if success else "Memory improvement failed"}
    except Exception as e:
        logger.error(f"Error improving memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Forget user data
@app.delete("/forget/{user_id}")
async def forget_user(user_id: str):
    """Forget all data for a user (GDPR compliance)."""
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        success = await agent.forget_user_data(user_id)
        return {"success": success, "message": f"Data for {user_id} forgotten" if success else "Failed to forget data"}
    except Exception as e:
        logger.error(f"Error forgetting user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get patterns
@app.get("/patterns/{user_id}")
async def get_patterns(user_id: str, time_window: Optional[str] = None):
    """Get emotional patterns for a user."""
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        patterns = await agent.get_emotional_patterns(
            user_id=user_id,
            time_window=time_window
        )
        return patterns
    except Exception as e:
        logger.error(f"Error getting patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
