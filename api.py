"""
EmoMemory Production API

FastAPI application with authentication, wallet system, and ChatGPT-like interface.
"""

from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import asyncio

from config import settings
from database import db, User, UserSession, ChatMessage, TransactionType
from auth import (
    auth_service, get_current_active_user,
    UserRegister, UserLogin, Token, UserProfile
)
from memory_emotion_agent import create_memory_agent, MemoryAwareEmotionAgent

# Initialize FastAPI
app = FastAPI(
    title=settings.app.app_name,
    version=settings.app.version,
    description="Memory-Enabled Emotion AI powered by Cognee",
    docs_url="/api/docs" if settings.app.debug else None
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global emotion agent (initialized on startup)
emotion_agent: Optional[MemoryAwareEmotionAgent] = None


# Pydantic models for API

class ChatRequest(BaseModel):
    """Chat message request."""
    message: str = Field(..., min_length=1, max_length=5000)
    session_id: Optional[str] = None
    input_type: str = Field(default="text", pattern="^(text|audio|video|image)$")
    context_description: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat message response."""
    session_id: str
    message_id: int
    emotion: str
    confidence: float
    sentiment_score: Optional[float] = None
    has_memory_context: bool
    memory_contexts_used: int
    credits_used: float
    timestamp: datetime


class SessionListResponse(BaseModel):
    """User sessions list."""
    sessions: List[Dict[str, Any]]
    total: int


class WalletInfo(BaseModel):
    """Wallet information."""
    balance: float
    lifetime_spent: float
    lifetime_purchased: float
    currency: str


class CreditPurchaseRequest(BaseModel):
    """Credit purchase request."""
    amount: float = Field(..., gt=0, description="USD amount to spend")
    payment_method: str = Field(..., description="Payment method ID from Stripe/PayPal")


class SubscriptionRequest(BaseModel):
    """Subscription change request."""
    plan: str = Field(..., pattern="^(free|starter|professional|enterprise)$")


class UsageStatsResponse(BaseModel):
    """Usage statistics."""
    total_predictions: int
    total_chats: int
    total_credits_used: float
    this_month_credits: float
    average_emotion_confidence: float


# Startup event

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    global emotion_agent
    
    print(f"🚀 Starting {settings.app.app_name} v{settings.app.version}")
    print(f"   Environment: {settings.app.environment}")
    print(f"   Cognee Cloud: {'Enabled' if settings.cognee.use_cloud else 'Local'}")
    
    # Initialize database
    try:
        db.create_tables()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")
    
    # Initialize emotion agent
    try:
        emotion_agent = await create_memory_agent(
            agent_type="multimodal",
            api_key=settings.cognee.api_key if settings.cognee.use_cloud else None,
            use_cloud=settings.cognee.use_cloud
        )
        print("✅ Emotion agent initialized")
    except Exception as e:
        print(f"❌ Failed to initialize emotion agent: {e}")
        emotion_agent = None


# Authentication endpoints

@app.post("/api/auth/register", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """Register a new user."""
    user = auth_service.register_user(
        email=user_data.email,
        username=user_data.username,
        password=user_data.password,
        full_name=user_data.full_name
    )
    return auth_service.get_user_profile(user)


@app.post("/api/auth/login", response_model=Token)
async def login(login_data: UserLogin):
    """Login and get access tokens."""
    return auth_service.login_user(login_data.email, login_data.password)


@app.post("/api/auth/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    """Refresh access token."""
    return auth_service.refresh_access_token(refresh_token)


@app.get("/api/auth/me", response_model=UserProfile)
async def get_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user profile."""
    return auth_service.get_user_profile(current_user)


# Chat endpoints (ChatGPT-like interface)

@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Send a chat message and get emotion analysis with memory."""
    
    if not emotion_agent:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Emotion agent not initialized"
        )
    
    # Check credits
    cost = settings.wallet.cost_per_chat_message
    if not current_user.has_sufficient_credits(cost):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient credits. Need {cost}, have {current_user.wallet.balance}"
        )
    
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    db_session = db.get_session()
    
    try:
        user_session = db_session.query(UserSession).filter(
            UserSession.session_id == session_id,
            UserSession.user_id == current_user.id
        ).first()
        
        if not user_session:
            user_session = UserSession(
                user_id=current_user.id,
                session_id=session_id,
                title=request.message[:50] + "..." if len(request.message) > 50 else request.message
            )
            db_session.add(user_session)
            db_session.commit()
            db_session.refresh(user_session)
        
        # Make prediction with memory
        result = await emotion_agent.predict_emotion(
            input_data=request.message,
            user_id=str(current_user.id),
            input_type=request.input_type,
            session_id=session_id,
            context_description=request.context_description or request.message,
            return_memory_context=True
        )
        
        # Save user message
        user_message = ChatMessage(
            session_id=user_session.id,
            role="user",
            content=request.message
        )
        db_session.add(user_message)
        
        # Save assistant response
        assistant_message = ChatMessage(
            session_id=user_session.id,
            role="assistant",
            content=f"Detected: {result['emotion']}",
            emotion_label=result["emotion"],
            emotion_confidence=result["confidence"],
            sentiment_score=result.get("sentiment_score"),
            had_memory_context=result.get("stateful", False),
            memory_contexts_used=result.get("memory_context", {}).get("context_count", 0) if result.get("stateful") else 0
        )
        db_session.add(assistant_message)
        
        # Update session stats
        user_session.message_count += 2
        user_session.total_credits_used += cost
        user_session.last_activity = datetime.utcnow()
        
        # Deduct credits
        db.log_usage(
            user_id=current_user.id,
            operation_type="chat",
            credits_used=cost,
            session_id=user_session.id,
            input_type=request.input_type,
            success=True
        )
        
        db_session.commit()
        
        return ChatResponse(
            session_id=session_id,
            message_id=assistant_message.id,
            emotion=result["emotion"],
            confidence=result["confidence"],
            sentiment_score=result.get("sentiment_score"),
            has_memory_context=result.get("stateful", False),
            memory_contexts_used=result.get("memory_context", {}).get("context_count", 0) if result.get("stateful") else 0,
            credits_used=cost,
            timestamp=datetime.utcnow()
        )
        
    finally:
        db_session.close()


@app.get("/api/chat/sessions", response_model=SessionListResponse)
async def list_sessions(
    current_user: User = Depends(get_current_active_user),
    limit: int = 20,
    offset: int = 0
):
    """List user's chat sessions."""
    session = db.get_session()
    
    try:
        sessions = session.query(UserSession).filter(
            UserSession.user_id == current_user.id
        ).order_by(UserSession.last_activity.desc()).offset(offset).limit(limit).all()
        
        total = session.query(UserSession).filter(
            UserSession.user_id == current_user.id
        ).count()
        
        return SessionListResponse(
            sessions=[
                {
                    "session_id": s.session_id,
                    "title": s.title,
                    "message_count": s.message_count,
                    "credits_used": s.total_credits_used,
                    "last_activity": s.last_activity,
                    "created_at": s.created_at
                }
                for s in sessions
            ],
            total=total
        )
        
    finally:
        session.close()


@app.get("/api/chat/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get messages from a specific session."""
    session = db.get_session()
    
    try:
        user_session = session.query(UserSession).filter(
            UserSession.session_id == session_id,
            UserSession.user_id == current_user.id
        ).first()
        
        if not user_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        messages = session.query(ChatMessage).filter(
            ChatMessage.session_id == user_session.id
        ).order_by(ChatMessage.created_at).all()
        
        return {
            "session_id": session_id,
            "messages": [
                {
                    "id": m.id,
                    "role": m.role,
                    "content": m.content,
                    "emotion": m.emotion_label,
                    "confidence": m.emotion_confidence,
                    "had_memory": m.had_memory_context,
                    "created_at": m.created_at
                }
                for m in messages
            ]
        }
        
    finally:
        session.close()


@app.delete("/api/chat/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete a chat session."""
    session = db.get_session()
    
    try:
        user_session = session.query(UserSession).filter(
            UserSession.session_id == session_id,
            UserSession.user_id == current_user.id
        ).first()
        
        if not user_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        session.delete(user_session)
        session.commit()
        
        return {"message": "Session deleted successfully"}
        
    finally:
        session.close()


# Wallet endpoints

@app.get("/api/wallet", response_model=WalletInfo)
async def get_wallet(current_user: User = Depends(get_current_active_user)):
    """Get wallet information."""
    if not current_user.wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    
    return WalletInfo(
        balance=current_user.wallet.balance,
        lifetime_spent=current_user.wallet.lifetime_spent,
        lifetime_purchased=current_user.wallet.lifetime_purchased,
        currency=settings.wallet.currency
    )


@app.post("/api/wallet/purchase")
async def purchase_credits(
    request: CreditPurchaseRequest,
    current_user: User = Depends(get_current_active_user),
    background_tasks: BackgroundTasks = None
):
    """Purchase credits (integrate with Stripe/PayPal)."""
    
    # TODO: Integrate with actual payment gateway (Stripe, PayPal, etc.)
    # This is a placeholder implementation
    
    credits_to_add = request.amount * 10  # $1 = 10 credits (example rate)
    
    session = db.get_session()
    try:
        # Add credits
        current_user.wallet.add_credits(credits_to_add, TransactionType.CREDIT_PURCHASE)
        
        # Log transaction
        from database import Transaction
        transaction = Transaction(
            user_id=current_user.id,
            transaction_type=TransactionType.CREDIT_PURCHASE,
            amount=request.amount,
            description=f"Purchased {credits_to_add} credits",
            payment_id=f"demo_{uuid.uuid4().hex[:16]}",
            payment_status="completed"
        )
        session.add(transaction)
        session.commit()
        
        return {
            "success": True,
            "credits_added": credits_to_add,
            "new_balance": current_user.wallet.balance,
            "transaction_id": transaction.id
        }
        
    finally:
        session.close()


@app.get("/api/wallet/transactions")
async def get_transactions(
    current_user: User = Depends(get_current_active_user),
    limit: int = 20,
    offset: int = 0
):
    """Get transaction history."""
    session = db.get_session()
    
    try:
        from database import Transaction
        transactions = session.query(Transaction).filter(
            Transaction.user_id == current_user.id
        ).order_by(Transaction.created_at.desc()).offset(offset).limit(limit).all()
        
        return {
            "transactions": [
                {
                    "id": t.id,
                    "type": t.transaction_type.value,
                    "amount": t.amount,
                    "description": t.description,
                    "status": t.payment_status,
                    "created_at": t.created_at
                }
                for t in transactions
            ]
        }
        
    finally:
        session.close()


# Subscription endpoints

@app.get("/api/subscription/plans")
async def get_subscription_plans():
    """Get available subscription plans."""
    return {"plans": settings.wallet.plans}


@app.post("/api/subscription/change")
async def change_subscription(
    request: SubscriptionRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Change subscription plan."""
    
    # TODO: Integrate with payment gateway for recurring billing
    # This is a placeholder implementation
    
    from database import SubscriptionPlan
    
    plan_map = {
        "free": SubscriptionPlan.FREE,
        "starter": SubscriptionPlan.STARTER,
        "professional": SubscriptionPlan.PROFESSIONAL,
        "enterprise": SubscriptionPlan.ENTERPRISE
    }
    
    new_plan = plan_map.get(request.plan)
    if not new_plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan"
        )
    
    session = db.get_session()
    try:
        current_user.subscription_plan = new_plan
        current_user.subscription_start = datetime.utcnow()
        current_user.subscription_end = datetime.utcnow() + timedelta(days=30)
        
        session.commit()
        
        return {
            "success": True,
            "new_plan": request.plan,
            "message": f"Subscription changed to {settings.wallet.plans[request.plan]['name']}"
        }
        
    finally:
        session.close()


# Usage stats

@app.get("/api/stats/usage", response_model=UsageStatsResponse)
async def get_usage_stats(current_user: User = Depends(get_current_active_user)):
    """Get usage statistics."""
    session = db.get_session()
    
    try:
        from database import UsageLog
        from sqlalchemy import func
        
        # Total stats
        total_predictions = session.query(UsageLog).filter(
            UsageLog.user_id == current_user.id,
            UsageLog.operation_type == "predict"
        ).count()
        
        total_chats = session.query(UsageLog).filter(
            UsageLog.user_id == current_user.id,
            UsageLog.operation_type == "chat"
        ).count()
        
        total_credits = session.query(func.sum(UsageLog.credits_used)).filter(
            UsageLog.user_id == current_user.id
        ).scalar() or 0.0
        
        # This month stats
        from datetime import timedelta
        month_start = datetime.utcnow() - timedelta(days=30)
        
        month_credits = session.query(func.sum(UsageLog.credits_used)).filter(
            UsageLog.user_id == current_user.id,
            UsageLog.created_at >= month_start
        ).scalar() or 0.0
        
        return UsageStatsResponse(
            total_predictions=total_predictions,
            total_chats=total_chats,
            total_credits_used=total_credits,
            this_month_credits=month_credits,
            average_emotion_confidence=0.85  # Placeholder
        )
        
    finally:
        session.close()


# Health check

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app.version,
        "emotion_agent": "initialized" if emotion_agent else "not initialized",
        "cognee_cloud": settings.cognee.use_cloud
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.debug
    )
