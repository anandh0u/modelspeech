"""
Database Models and Management for EmoMemory SaaS

User accounts, wallet, transactions, and usage tracking.
"""

from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Boolean, 
    DateTime, ForeignKey, Text, JSON, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session, sessionmaker
from sqlalchemy.sql import func
import enum
from passlib.context import CryptContext

from config import settings


Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SubscriptionPlan(enum.Enum):
    """Subscription plan types."""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class TransactionType(enum.Enum):
    """Transaction types."""
    CREDIT_PURCHASE = "credit_purchase"
    SUBSCRIPTION = "subscription"
    USAGE = "usage"
    REFUND = "refund"
    FREE_CREDITS = "free_credits"


class User(Base):
    """User account model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    
    # Subscription
    subscription_plan = Column(SQLEnum(SubscriptionPlan), default=SubscriptionPlan.FREE)
    subscription_start = Column(DateTime)
    subscription_end = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    wallet = relationship("Wallet", back_populates="user", uselist=False)
    sessions = relationship("UserSession", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    usage_logs = relationship("UsageLog", back_populates="user")
    
    def verify_password(self, password: str) -> bool:
        """Verify password."""
        return pwd_context.verify(password, self.hashed_password)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password."""
        return pwd_context.hash(password)
    
    def has_sufficient_credits(self, amount: float) -> bool:
        """Check if user has sufficient credits."""
        return self.wallet and self.wallet.balance >= amount
    
    def is_subscription_active(self) -> bool:
        """Check if subscription is active."""
        if not self.subscription_end:
            return False
        return datetime.utcnow() < self.subscription_end


class Wallet(Base):
    """User wallet for credits."""
    __tablename__ = "wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    balance = Column(Float, default=0.0)  # Current credit balance
    lifetime_spent = Column(Float, default=0.0)  # Total credits spent
    lifetime_purchased = Column(Float, default=0.0)  # Total credits purchased
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="wallet")
    
    def add_credits(self, amount: float, transaction_type: TransactionType) -> bool:
        """Add credits to wallet."""
        if amount <= 0:
            return False
        
        self.balance += amount
        
        if transaction_type == TransactionType.CREDIT_PURCHASE:
            self.lifetime_purchased += amount
        
        return True
    
    def deduct_credits(self, amount: float) -> bool:
        """Deduct credits from wallet."""
        if amount <= 0 or self.balance < amount:
            return False
        
        self.balance -= amount
        self.lifetime_spent += amount
        return True


class Transaction(Base):
    """Transaction history."""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)  # Credits or USD
    currency = Column(String(10), default="USD")
    
    description = Column(Text)
    metadata = Column(JSON)  # Store additional data (payment gateway info, etc.)
    
    # Payment gateway info
    payment_id = Column(String(255))  # External payment ID
    payment_status = Column(String(50))  # pending, completed, failed, refunded
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="transactions")


class UsageLog(Base):
    """Usage tracking for analytics and billing."""
    __tablename__ = "usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("user_sessions.id"))
    
    operation_type = Column(String(50), nullable=False)  # predict, chat, recall, cognify
    input_type = Column(String(50))  # text, audio, video, image
    
    credits_used = Column(Float, nullable=False)
    
    # Performance metrics
    duration_ms = Column(Integer)  # Operation duration in milliseconds
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    # Additional data
    metadata = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="usage_logs")
    session = relationship("UserSession", back_populates="usage_logs")


class UserSession(Base):
    """User chat sessions with memory context."""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    title = Column(String(255))  # Auto-generated or user-defined
    
    # Session stats
    message_count = Column(Integer, default=0)
    total_credits_used = Column(Float, default=0.0)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    messages = relationship("ChatMessage", back_populates="session")
    usage_logs = relationship("UsageLog", back_populates="session")


class ChatMessage(Base):
    """Chat message history."""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("user_sessions.id"), nullable=False)
    
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    
    # Emotion analysis results
    emotion_label = Column(String(50))
    emotion_confidence = Column(Float)
    sentiment_score = Column(Float)
    
    # Memory context
    had_memory_context = Column(Boolean, default=False)
    memory_contexts_used = Column(Integer, default=0)
    
    # Metadata
    metadata = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("UserSession", back_populates="messages")


class APIKey(Base):
    """API keys for programmatic access."""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    key = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(100))  # User-friendly name
    
    is_active = Column(Boolean, default=True)
    
    # Rate limiting
    rate_limit_per_minute = Column(Integer)
    rate_limit_per_day = Column(Integer)
    
    last_used_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)  # Optional expiration


# Database connection and session management

class Database:
    """Database manager."""
    
    def __init__(self):
        """Initialize database connection."""
        self.engine = create_engine(
            settings.database.url,
            pool_size=settings.database.pool_size,
            echo=settings.database.echo
        )
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def create_tables(self):
        """Create all tables."""
        Base.metadata.create_all(bind=self.engine)
        print("✅ Database tables created")
    
    def drop_tables(self):
        """Drop all tables (use with caution!)."""
        Base.metadata.drop_all(bind=self.engine)
        print("⚠️  Database tables dropped")
    
    def get_session(self) -> Session:
        """Get database session."""
        return self.SessionLocal()
    
    def create_user(
        self,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None
    ) -> User:
        """Create a new user with wallet."""
        session = self.get_session()
        
        try:
            # Create user
            user = User(
                email=email,
                username=username,
                hashed_password=User.hash_password(password),
                full_name=full_name,
                subscription_plan=SubscriptionPlan.FREE
            )
            session.add(user)
            session.flush()
            
            # Create wallet with free credits
            wallet = Wallet(
                user_id=user.id,
                balance=settings.wallet.free_tier_credits
            )
            session.add(wallet)
            
            # Log free credits transaction
            transaction = Transaction(
                user_id=user.id,
                transaction_type=TransactionType.FREE_CREDITS,
                amount=settings.wallet.free_tier_credits,
                description="Welcome bonus credits",
                payment_status="completed"
            )
            session.add(transaction)
            
            session.commit()
            session.refresh(user)
            
            return user
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        session = self.get_session()
        try:
            return session.query(User).filter(User.email == email).first()
        finally:
            session.close()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        session = self.get_session()
        try:
            return session.query(User).filter(User.username == username).first()
        finally:
            session.close()
    
    def log_usage(
        self,
        user_id: int,
        operation_type: str,
        credits_used: float,
        session_id: Optional[int] = None,
        **kwargs
    ) -> UsageLog:
        """Log usage and deduct credits."""
        session = self.get_session()
        
        try:
            # Get user and wallet
            user = session.query(User).filter(User.id == user_id).first()
            if not user or not user.wallet:
                raise ValueError("User or wallet not found")
            
            # Deduct credits
            if not user.wallet.deduct_credits(credits_used):
                raise ValueError("Insufficient credits")
            
            # Create usage log
            usage_log = UsageLog(
                user_id=user_id,
                session_id=session_id,
                operation_type=operation_type,
                credits_used=credits_used,
                **kwargs
            )
            session.add(usage_log)
            
            session.commit()
            return usage_log
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


# Global database instance
db = Database()


if __name__ == "__main__":
    # Create tables
    db.create_tables()
    
    # Create demo user
    try:
        demo_user = db.create_user(
            email="demo@emomemory.app",
            username="demo",
            password="demo123",
            full_name="Demo User"
        )
        print(f"✅ Created demo user: {demo_user.email}")
        print(f"   Credits: {demo_user.wallet.balance}")
    except Exception as e:
        print(f"Demo user may already exist: {e}")
