# 🚀 Quick Start Guide - AI-Powered Code Reviewer

## 📋 Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- Docker & Docker Compose
- PostgreSQL 15 (or use Docker)
- Redis 7 (or use Docker)
- Git

## ⚡ Quick Setup (5 minutes)

### 1. Clone & Configure

```bash
cd "AI_Powered Code_Reviewer"

# Copy environment file
copy .env.example .env

# Edit .env with your API keys (CRITICAL!)
# - Add your OPENAI_API_KEY or GEMINI_API_KEY
# - Add your GITHUB_TOKEN
# - Change JWT_SECRET_KEY to a random string (32+ characters)
# - Update database passwords
```

### 2. Install Dependencies

```bash
# Backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
cd ..
```

### 3. Setup Database (Using Docker - EASIEST)

```bash
# Start all services (PostgreSQL, Redis, Prometheus, Grafana)
docker-compose up -d postgres redis

# Wait 10 seconds for services to start
timeout /t 10

# Run database migrations
alembic upgrade head

# Initialize knowledge base
python -m app.scripts.init_knowledge_base
```

### 4. Start the Application

**Option A: Using Docker (Recommended)**
```bash
docker-compose up -d
```

Access:
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin)

**Option B: Local Development**
```bash
# Terminal 1 - Backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

## 🔐 First Steps After Setup

### 1. Create Your First User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "github_username": "admin",
    "password": "SecurePassword123",
    "full_name": "Admin User"
  }'
```

### 2. Login & Get Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "SecurePassword123"
  }'
```

Save the `access_token` from the response!

### 3. Analyze Your First PR

```bash
curl -X POST "http://localhost:8000/api/v1/review/analyze" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "repository": "owner/repo",
    "pr_number": 123,
    "include_security_scan": true,
    "include_complexity_analysis": true
  }'
```

## 🧪 Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v
```

## 📊 Access Monitoring

### Prometheus Metrics
- URL: http://localhost:9090
- Query examples:
  - `rate(http_requests_total[5m])`
  - `histogram_quantile(0.95, http_request_duration_seconds_bucket)`
  - `code_quality_score`

### Grafana Dashboards
- URL: http://localhost:3001
- Login: admin / admin (change on first login)
- Datasource: Already configured (Prometheus)

## 🛠️ Useful Commands

```bash
# Using Make (if available)
make help              # Show all commands
make dev               # Start development servers
make test              # Run tests
make lint              # Run linting
make docker-up         # Start Docker containers
make docker-logs       # View logs
make migrate           # Run database migrations

# Manual Commands
docker-compose ps                    # Check service status
docker-compose logs -f backend       # View backend logs
docker-compose exec backend bash     # Shell into backend
docker-compose exec postgres psql -U postgres  # Database shell
```

## 🔧 Configuration

### Environment Variables (.env)

**Required:**
- `OPENAI_API_KEY` or `GEMINI_API_KEY` - For AI analysis
- `GITHUB_TOKEN` - For GitHub API access
- `JWT_SECRET_KEY` - For JWT token signing (32+ chars)

**Database:**
- `DATABASE_URL` - PostgreSQL connection string
- Default: `postgresql://postgres:postgres@localhost:5432/ai_code_review`

**Redis:**
- `REDIS_HOST` - Redis hostname (default: localhost)
- `REDIS_PORT` - Redis port (default: 6379)
- `REDIS_PASSWORD` - Redis password

**Optional:**
- `DEBUG` - Enable debug mode (default: false)
- `LOG_LEVEL` - Logging level (default: INFO)
- `AI_PROVIDER` - openai or gemini (default: openai)

## 🐛 Troubleshooting

### Database Connection Error
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

### Redis Connection Error
```bash
# Check if Redis is running
docker-compose ps redis

# Test Redis connection
docker-compose exec redis redis-cli ping
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Port Already in Use
```bash
# Windows - Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <PID> /F
```

### Docker Issues
```bash
# Clean rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## 📚 Next Steps

1. **Configure GitHub App**
   - Create a GitHub App in your org/account
   - Add webhook URL: `https://yourdomain.com/api/v1/webhooks/github`
   - Subscribe to: `pull_request`, `push`, `issues`
   - Update `.env` with `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET`

2. **Setup Webhooks**
   - Repository Settings → Webhooks
   - Add webhook: `https://yourdomain.com/api/v1/webhooks/github`
   - Content type: `application/json`
   - Secret: Your `GITHUB_WEBHOOK_SECRET`

3. **Create API Keys**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/api-keys" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name": "My API Key", "expires_in_days": 90}'
   ```

4. **Explore API Documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## 🚀 Deployment to Production

### Using Docker

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### Environment Setup

1. Update production `.env`:
   - Set `DEBUG=false`
   - Use strong passwords
   - Configure proper CORS origins
   - Setup SSL certificates

2. Setup Nginx with SSL:
   - Place SSL certificates in `nginx/ssl/`
   - Uncomment HTTPS configuration in `nginx/nginx.conf`

3. Configure monitoring:
   - Setup Prometheus alerts
   - Configure Grafana dashboards
   - Setup log aggregation

## 📞 Support & Resources

- **API Documentation:** http://localhost:8000/docs
- **Implementation Progress:** See IMPLEMENTATION_PROGRESS.md
- **Metrics Dashboard:** http://localhost:3001
- **Health Check:** http://localhost:8000/api/v1/health

## ✅ Verify Installation

```bash
# Check backend health
curl http://localhost:8000/api/v1/health

# Check metrics
curl http://localhost:8000/metrics

# Check database
docker-compose exec backend python -c "from app.db.database import engine; print('DB OK')"

# Check Redis
docker-compose exec redis redis-cli ping
```

---

**🎉 You're all set! Happy coding!**

For detailed implementation progress and features, see [IMPLEMENTATION_PROGRESS.md](IMPLEMENTATION_PROGRESS.md)
