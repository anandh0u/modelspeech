# 🚀 EmoMemory Production Deployment Guide

Complete guide to deploy EmoMemory as a production SaaS platform with Cognee Cloud integration.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Cognee Cloud Setup](#cognee-cloud-setup)
4. [Database Setup](#database-setup)
5. [Docker Deployment](#docker-deployment)
6. [Cloud Deployment Options](#cloud-deployment-options)
7. [Payment Integration](#payment-integration)
8. [Monitoring & Scaling](#monitoring--scaling)

---

## 🔧 Prerequisites

### Required Services

- **Cognee Cloud Account** ($35 Developer Plan) - Get API key from [cognee.ai](https://cognee.ai)
- **PostgreSQL Database** - Version 12+
- **Domain Name** - For production hosting
- **Payment Gateway** - Stripe or PayPal account
- **Email Service** - SMTP or SendGrid (optional)

### Software Requirements

```bash
- Python 3.9+
- Docker & Docker Compose
- Git
- PostgreSQL client tools
```

---

## 🏠 Local Development Setup

### 1. Clone and Setup Environment

```bash
# Clone repository
git clone <your-repo-url>
cd modelspeech

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your values
notepad .env  # Windows
nano .env     # Linux/Mac
```

**Required Configuration:**

```env
# Cognee Cloud
COGNEE_API_KEY=your_api_key_here
COGNEE_USE_CLOUD=true

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/emomemory

# Security
SECRET_KEY=generate-a-random-secret-key-32chars
```

### 3. Initialize Database

```bash
# Create database tables
python database.py

# This will:
# - Create all tables
# - Create demo user (demo@emomemory.app / demo123)
# - Add free credits to demo wallet
```

### 4. Run Development Servers

**Terminal 1 - Backend API:**
```bash
uvicorn api:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
python frontend_app.py
```

**Access:**
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs
- Frontend: http://localhost:7860

---

## ☁️ Cognee Cloud Setup

### 1. Get API Key

1. Sign up at [cognee.ai](https://cognee.ai)
2. Choose **Developer Plan** ($35/month)
3. Go to Dashboard → API Keys
4. Create new API key
5. Copy the key

### 2. Configure Cognee

```python
# In .env file
COGNEE_API_KEY=your_key_here
COGNEE_API_URL=https://api.cognee.ai
COGNEE_DATASET=emomemory_production
COGNEE_USE_CLOUD=true
```

### 3. Test Connection

```python
# test_cognee.py
import asyncio
import cognee

async def test():
    cognee.config.set_api_key("your_key_here")
    
    # Test adding data
    await cognee.add("Test memory", dataset_name="test")
    
    # Test search
    results = await cognee.search("test", dataset_name="test")
    print(f"✅ Cognee Cloud working! Found {len(results)} results")

asyncio.run(test())
```

### 4. Dataset Management

Your app will automatically create and manage datasets:
- `emomemory_production` - Main production data
- User-specific datasets for isolation (optional)

**Monitor usage** in Cognee Cloud dashboard:
- API calls
- Storage used
- Query performance

---

## 💾 Database Setup

### Option 1: Local PostgreSQL

```bash
# Install PostgreSQL
# Windows: Download from postgresql.org
# Mac: brew install postgresql
# Linux: sudo apt-get install postgresql

# Create database
psql -U postgres
CREATE DATABASE emomemory;
CREATE USER emomemory WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE emomemory TO emomemory;
\q

# Configure DATABASE_URL
DATABASE_URL=postgresql://emomemory:your_password@localhost:5432/emomemory
```

### Option 2: Cloud Database

**Heroku Postgres:**
```bash
heroku addons:create heroku-postgresql:mini
DATABASE_URL=$(heroku config:get DATABASE_URL)
```

**AWS RDS:**
```bash
# Create RDS PostgreSQL instance in AWS console
DATABASE_URL=postgresql://user:pass@your-rds-endpoint:5432/emomemory
```

**Railway.app:**
```bash
# Add PostgreSQL plugin in Railway dashboard
# Copy connection string from dashboard
```

### Initialize Schema

```bash
python database.py
```

---

## 🐳 Docker Deployment

### 1. Build and Run with Docker Compose

```bash
# Create .env file with your configuration
cp .env.example .env
# Edit .env with your values

# Build and start all services
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Services Started:**
- `postgres` - PostgreSQL database
- `redis` - Redis cache
- `api` - FastAPI backend (port 8000)
- `frontend` - Gradio UI (port 7860)
- `nginx` - Reverse proxy (port 80/443)

### 2. Access Services

- Frontend: http://localhost:7860
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

### 3. Docker Commands

```bash
# View logs
docker-compose logs -f api
docker-compose logs -f frontend

# Restart service
docker-compose restart api

# Rebuild after code changes
docker-compose build api
docker-compose up -d api

# Execute commands in container
docker-compose exec api python database.py
docker-compose exec postgres psql -U emomemory
```

---

## 🌍 Cloud Deployment Options

### Option 1: Railway.app (Recommended)

**Easiest deployment with automatic HTTPS**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create new project
railway init

# Add PostgreSQL
railway add --plugin postgresql

# Add environment variables
railway variables set COGNEE_API_KEY=your_key
railway variables set SECRET_KEY=your_secret

# Deploy
railway up
```

**Custom domain:**
```bash
railway domain  # Get railway.app subdomain
# Or add custom domain in Railway dashboard
```

### Option 2: Heroku

```bash
# Install Heroku CLI
# Login
heroku login

# Create app
heroku create emomemory

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set COGNEE_API_KEY=your_key
heroku config:set SECRET_KEY=your_secret
heroku config:set COGNEE_USE_CLOUD=true

# Deploy
git push heroku main

# Scale
heroku ps:scale web=1

# View logs
heroku logs --tail
```

### Option 3: AWS (EC2 + RDS)

**1. Launch EC2 Instance**
- Instance type: t2.medium or larger
- OS: Ubuntu 22.04 LTS
- Security groups: Allow ports 22, 80, 443

**2. SSH and Setup**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo apt-get install docker-compose

# Clone repo
git clone your-repo-url
cd modelspeech

# Configure .env
nano .env

# Deploy
docker-compose up -d
```

**3. Setup Domain**
- Point A record to EC2 IP
- Setup SSL with Let's Encrypt (see below)

### Option 4: DigitalOcean App Platform

```bash
# Create app.yaml
cat > app.yaml << EOF
name: emomemory
services:
  - name: api
    github:
      repo: your-username/emomemory
      branch: main
    dockerfile_path: Dockerfile
    http_port: 8000
    envs:
      - key: COGNEE_API_KEY
        value: your_key
    health_check:
      http_path: /api/health
    
databases:
  - name: postgres
    engine: PG
    version: "15"
EOF

# Deploy via dashboard or CLI
doctl apps create --spec app.yaml
```

---

## 💳 Payment Integration

### Stripe Integration

**1. Setup Stripe Account**
```bash
# Sign up at stripe.com
# Get API keys from Dashboard → Developers → API keys
```

**2. Install Stripe SDK**
```bash
pip install stripe
```

**3. Add to api.py**
```python
import stripe

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.post("/api/wallet/purchase/stripe")
async def purchase_with_stripe(
    amount: float,
    payment_method_id: str,
    current_user: User = Depends(get_current_active_user)
):
    try:
        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to cents
            currency="usd",
            payment_method=payment_method_id,
            confirm=True
        )
        
        # Add credits
        credits = amount * 10  # $1 = 10 credits
        current_user.wallet.add_credits(credits, TransactionType.CREDIT_PURCHASE)
        
        return {"success": True, "credits_added": credits}
        
    except stripe.error.CardError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

**4. Frontend Integration**
```javascript
// Add Stripe.js to frontend
<script src="https://js.stripe.com/v3/"></script>

// Initialize
const stripe = Stripe('pk_test_...');

// Create payment
const {paymentMethod} = await stripe.createPaymentMethod({
    type: 'card',
    card: cardElement,
});

// Send to backend
await fetch('/api/wallet/purchase/stripe', {
    method: 'POST',
    body: JSON.stringify({
        amount: 10.0,
        payment_method_id: paymentMethod.id
    })
});
```

### PayPal Integration

Similar process with PayPal SDK:
```bash
pip install paypalrestsdk
```

---

## 🔒 Security Checklist

### Environment Configuration

- [ ] Generate strong SECRET_KEY (32+ random characters)
- [ ] Use HTTPS in production (SSL certificate)
- [ ] Set DEBUG=false in production
- [ ] Restrict CORS origins
- [ ] Use environment variables (never commit secrets)

### Database Security

- [ ] Strong database password
- [ ] Database firewall rules (allow only app IP)
- [ ] Regular backups
- [ ] Encrypted connections (SSL)

### API Security

- [ ] Rate limiting enabled
- [ ] JWT token expiration configured
- [ ] Input validation on all endpoints
- [ ] SQL injection protection (using SQLAlchemy ORM)
- [ ] XSS protection headers

### Monitoring

- [ ] Error tracking (Sentry)
- [ ] Uptime monitoring
- [ ] Log aggregation
- [ ] Performance monitoring

---

## 📊 Monitoring & Scaling

### Setup Monitoring

**1. Sentry for Error Tracking**
```bash
pip install sentry-sdk

# In api.py
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")
```

**2. Prometheus for Metrics**
```bash
pip install prometheus-fastapi-instrumentator

# In api.py
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

**3. Health Checks**
```python
# Already implemented at /api/health
# Monitor this endpoint with:
# - UptimeRobot
# - Pingdom
# - AWS CloudWatch
```

### Scaling Strategies

**Vertical Scaling:**
```bash
# Increase server resources
# Docker: Adjust container limits
# Cloud: Choose larger instance type
```

**Horizontal Scaling:**
```bash
# Run multiple API instances behind load balancer

# docker-compose.yml
services:
  api:
    replicas: 3  # Run 3 instances
    
  nginx:
    # Add load balancing config
```

**Database Scaling:**
```bash
# Add read replicas
# Use connection pooling
# Implement caching with Redis
```

**Cognee Scaling:**
```bash
# Upgrade Cognee Cloud plan as needed:
# - Developer: $35/month
# - Professional: $99/month
# - Enterprise: Custom pricing
```

---

## 🔥 Production Checklist

### Pre-Launch

- [ ] All environment variables configured
- [ ] Database initialized and backed up
- [ ] Cognee Cloud API key tested
- [ ] Payment gateway tested (test mode)
- [ ] Email service configured
- [ ] SSL certificate installed
- [ ] Domain name configured
- [ ] CORS origins set correctly
- [ ] Rate limiting configured
- [ ] Error tracking enabled

### Launch

- [ ] Deploy to production
- [ ] Test all endpoints
- [ ] Test authentication flow
- [ ] Test payment flow
- [ ] Test chat functionality
- [ ] Test memory operations
- [ ] Load testing completed
- [ ] Monitoring dashboards setup

### Post-Launch

- [ ] Monitor error rates
- [ ] Check API performance
- [ ] Monitor Cognee usage
- [ ] Track user signups
- [ ] Monitor payment success rate
- [ ] Regular database backups
- [ ] Security updates applied

---

## 🆘 Troubleshooting

### Common Issues

**"Cognee API key invalid"**
```bash
# Check API key in .env
# Verify Cognee Cloud subscription active
# Test connection with test script
```

**"Database connection failed"**
```bash
# Check DATABASE_URL format
# Verify PostgreSQL is running
# Test connection: psql $DATABASE_URL
```

**"Insufficient credits"**
```bash
# Check user wallet balance
# Verify transaction was recorded
# Check usage logs in database
```

**"CORS errors"**
```bash
# Add frontend URL to ALLOWED_ORIGINS in .env
# Restart API server after changes
```

### Logs

```bash
# Docker logs
docker-compose logs -f api

# Application logs
tail -f logs/app.log

# Database logs
docker-compose logs postgres
```

---

## 📧 Support

- **Documentation:** README.md, HACKATHON_SUBMISSION.md
- **Issues:** GitHub Issues
- **Email:** support@emomemory.app
- **Cognee Support:** support@cognee.ai

---

<div align="center">

**🚀 Ready to Deploy!**

Your EmoMemory SaaS platform is ready for the world!

</div>
