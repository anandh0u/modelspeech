"""
Configuration Management for EmoMemory SaaS Platform
"""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class CogneeConfig:
    """Cognee Cloud configuration."""
    api_key: str
    api_url: str = "https://api.cognee.ai"
    dataset_name: str = "emomemory_production"
    use_cloud: bool = True
    timeout: int = 30


@dataclass
class DatabaseConfig:
    """Database configuration for user management."""
    url: str
    pool_size: int = 10
    echo: bool = False


@dataclass
class WalletConfig:
    """Wallet and billing configuration."""
    currency: str = "USD"
    free_tier_credits: float = 10.0  # Free credits for new users
    
    # Pricing per operation (in credits)
    cost_per_prediction: float = 0.1
    cost_per_chat_message: float = 0.05
    cost_per_memory_query: float = 0.02
    cost_per_cognify: float = 1.0
    
    # Subscription plans
    plans: dict = None
    
    def __post_init__(self):
        if self.plans is None:
            self.plans = {
                "free": {
                    "name": "Free Tier",
                    "price": 0.0,
                    "monthly_credits": 100,
                    "features": ["Basic emotion detection", "Limited memory", "Standard support"]
                },
                "starter": {
                    "name": "Starter",
                    "price": 9.99,
                    "monthly_credits": 1000,
                    "features": ["All emotion models", "Full memory", "Email support", "API access"]
                },
                "professional": {
                    "name": "Professional",
                    "price": 49.99,
                    "monthly_credits": 10000,
                    "features": ["Everything in Starter", "Priority support", "Advanced analytics", "Custom integrations"]
                },
                "enterprise": {
                    "name": "Enterprise",
                    "price": 199.99,
                    "monthly_credits": 100000,
                    "features": ["Everything in Professional", "Dedicated support", "SLA", "On-premise option"]
                }
            }


@dataclass
class AuthConfig:
    """Authentication configuration."""
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    refresh_token_expire_days: int = 7


@dataclass
class AppConfig:
    """Main application configuration."""
    app_name: str = "EmoMemory"
    version: str = "1.0.0"
    environment: str = "production"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Feature flags
    enable_authentication: bool = True
    enable_wallet: bool = True
    enable_analytics: bool = True
    enable_rate_limiting: bool = True
    
    # Rate limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    
    # CORS
    allowed_origins: list = None
    
    def __post_init__(self):
        if self.allowed_origins is None:
            self.allowed_origins = [
                "http://localhost:3000",
                "http://localhost:8000",
                "https://emomemory.app",  # Your production domain
            ]


class Settings:
    """Global settings manager."""
    
    def __init__(self):
        """Initialize settings from environment variables."""
        
        # Cognee Configuration
        self.cognee = CogneeConfig(
            api_key=os.getenv("COGNEE_API_KEY", ""),
            api_url=os.getenv("COGNEE_API_URL", "https://api.cognee.ai"),
            dataset_name=os.getenv("COGNEE_DATASET", "emomemory_production"),
            use_cloud=os.getenv("COGNEE_USE_CLOUD", "true").lower() == "true"
        )
        
        # Database Configuration
        self.database = DatabaseConfig(
            url=os.getenv(
                "DATABASE_URL",
                "postgresql://user:password@localhost:5432/emomemory"
            )
        )
        
        # Wallet Configuration
        self.wallet = WalletConfig(
            currency=os.getenv("WALLET_CURRENCY", "USD"),
            free_tier_credits=float(os.getenv("FREE_TIER_CREDITS", "10.0"))
        )
        
        # Auth Configuration
        self.auth = AuthConfig(
            secret_key=os.getenv("SECRET_KEY", "your-secret-key-change-in-production"),
            algorithm=os.getenv("JWT_ALGORITHM", "HS256")
        )
        
        # App Configuration
        self.app = AppConfig(
            environment=os.getenv("ENVIRONMENT", "production"),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8000"))
        )
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate configuration.
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check Cognee API key
        if self.cognee.use_cloud and not self.cognee.api_key:
            errors.append("COGNEE_API_KEY is required when using Cognee Cloud")
        
        # Check secret key in production
        if self.app.environment == "production" and self.auth.secret_key == "your-secret-key-change-in-production":
            errors.append("SECRET_KEY must be changed in production")
        
        # Check database URL
        if not self.database.url:
            errors.append("DATABASE_URL is required")
        
        return len(errors) == 0, errors


# Global settings instance
settings = Settings()


# Validate on import
is_valid, errors = settings.validate()
if not is_valid and os.getenv("SKIP_CONFIG_VALIDATION") != "true":
    print("⚠️  Configuration Warnings:")
    for error in errors:
        print(f"   - {error}")
    print("\nSet SKIP_CONFIG_VALIDATION=true to skip this check")
