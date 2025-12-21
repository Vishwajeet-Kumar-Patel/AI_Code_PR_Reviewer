# 🧪 Complete Testing & Feature Verification Guide

## 📋 All 45+ Features Checklist

### **Phase 1: Production Readiness (15 Features)**

#### 1.1 Authentication & Authorization (7 Features)
- [ ] **JWT Authentication** - POST `/api/v1/auth/login`
- [ ] **User Registration** - POST `/api/v1/auth/register`
- [ ] **Token Refresh** - POST `/api/v1/auth/refresh`
- [ ] **OAuth2 GitHub** - GET `/api/v1/auth/github/login`
- [ ] **API Key Generation** - POST `/api/v1/auth/api-keys`
- [ ] **Role-Based Access** - Check user roles (user/admin/super_admin)
- [ ] **Password Change** - POST `/api/v1/auth/change-password`

#### 1.2 CI/CD & Docker (4 Features)
- [ ] **GitHub Actions CI/CD** - Check `.github/workflows/`
- [ ] **Docker Compose** - `docker-compose up`
- [ ] **Multi-stage Docker Build** - Check `Dockerfile`
- [ ] **Nginx Reverse Proxy** - Access via `http://localhost`

#### 1.3 Monitoring & Testing (4 Features)
- [ ] **Prometheus Metrics** - GET `/metrics`
- [ ] **Health Check** - GET `/health`
- [ ] **Test Suite** - `pytest tests/ -v`
- [ ] **Code Coverage** - `pytest --cov=app`

---

### **Phase 2: Advanced Features (10 Features)**

#### 2.1 GitHub Integration (5 Features)
- [ ] **Webhook Handler** - POST `/api/v1/webhooks/github`
- [ ] **PR Analysis** - Trigger on PR events
- [ ] **Auto PR Comments** - Check GitHub PR comments
- [ ] **Push Event Handling** - Trigger on push events
- [ ] **Issue Event Handling** - Trigger on issue events

#### 2.2 Real-time & Caching (5 Features)
- [ ] **WebSocket Connection** - WS `/ws/{client_id}`
- [ ] **Real-time Progress** - Subscribe to review updates
- [ ] **Redis Caching** - Check cache hit/miss
- [ ] **Advanced AI Fixes** - POST `/api/v1/review/generate-fix`
- [ ] **Auto-PR Creation** - POST `/api/v1/review/create-fix-pr`

---

### **Phase 3: Differentiation (12 Features)**

#### 3.1 Plugin System (4 Features)
- [ ] **List Plugins** - GET `/api/v1/plugins`
- [ ] **Enable Plugin** - POST `/api/v1/plugins/{plugin_id}/enable`
- [ ] **Custom Plugins** - Upload new plugin
- [ ] **Plugin Execution** - Check in review results

#### 3.2 Multi-tenancy (4 Features)
- [ ] **Create Organization** - POST `/api/v1/organizations`
- [ ] **Invite Members** - POST `/api/v1/organizations/{id}/invite`
- [ ] **Role Management** - PATCH `/api/v1/organizations/{id}/members`
- [ ] **Quota Management** - Check organization limits

#### 3.3 Advanced Security (4 Features)
- [ ] **Secrets Scanner** - POST `/api/v1/security/scan-secrets`
- [ ] **Dependency Check** - POST `/api/v1/security/check-dependencies`
- [ ] **SBOM Generation** - POST `/api/v1/security/generate-sbom`
- [ ] **Compliance Check** - POST `/api/v1/security/compliance-check`

---

### **Phase 4: Enterprise (8+ Features)**

#### 4.1 Analytics & Reporting (4 Features)
- [ ] **Dashboard Stats** - GET `/api/v1/analytics/dashboard`
- [ ] **Repository Analytics** - GET `/api/v1/analytics/repository/{repo_id}`
- [ ] **Team Metrics** - GET `/api/v1/analytics/team/{org_id}`
- [ ] **Trend Analysis** - GET `/api/v1/analytics/trends`

#### 4.2 Infrastructure & Deployment (4 Features)
- [ ] **Terraform AWS** - Apply in `terraform/aws/`
- [ ] **Kubernetes Deploy** - Apply in `k8s/`
- [ ] **Auto-scaling** - Check HPA configuration
- [ ] **Load Balancing** - Check service distribution

---

## 🚀 Step-by-Step Testing Guide

### Step 1: Environment Setup (5 minutes)

```powershell
# 1. Activate virtual environment
cd "c:\Users\vishw\OneDrive\Desktop\AI_Powered Code_Reviewer"
.\.venv\Scripts\activate

# 2. Verify environment variables
Get-Content .env | Select-String "GITHUB_TOKEN|OPENAI|DATABASE"

# 3. Install/verify dependencies
pip install -r requirements.txt

# 4. Check database
python -c "from app.core.config import Settings; print(Settings().DATABASE_URL)"
```

### Step 2: Database Initialization (3 minutes)

```powershell
# Initialize database
python -m app.scripts.init_database

# Initialize knowledge base
python -m app.scripts.init_knowledge_base

# Verify database
python -c "from app.db.database import engine; from sqlalchemy import inspect; print(inspect(engine).get_table_names())"
```

### Step 3: Start Services (2 minutes)

```powershell
# Option A: Start with uvicorn (Development)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Option B: Start with Docker Compose (Recommended)
docker-compose up -d
```

### Step 4: Basic API Tests (10 minutes)

#### 4.1 Health Check
```powershell
curl http://localhost:8000/health
```

**Expected Response:**
```json
{"status": "healthy", "version": "1.0.0"}
```

#### 4.2 Register User
```powershell
$body = @{
    email = "test@example.com"
    username = "testuser"
    password = "SecurePass123!"
    full_name = "Test User"
} | ConvertTo-Json

curl -X POST "http://localhost:8000/api/v1/auth/register" `
  -H "Content-Type: application/json" `
  -d $body
```

#### 4.3 Login & Get Token
```powershell
$loginBody = @{
    username = "test@example.com"
    password = "SecurePass123!"
} | ConvertTo-Json

$response = curl -X POST "http://localhost:8000/api/v1/auth/login" `
  -H "Content-Type: application/json" `
  -d $loginBody | ConvertFrom-Json

$token = $response.access_token
Write-Host "Token: $token"
```

#### 4.4 Test Protected Endpoint
```powershell
curl -H "Authorization: Bearer $token" `
  http://localhost:8000/api/v1/auth/me
```

### Step 5: Core Feature Tests (20 minutes)

#### 5.1 Create Repository
```powershell
$repoBody = @{
    name = "test-repo"
    full_name = "username/test-repo"
    github_url = "https://github.com/username/test-repo"
} | ConvertTo-Json

curl -X POST "http://localhost:8000/api/v1/repository" `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d $repoBody
```

#### 5.2 Submit Code for Review
```powershell
$reviewBody = @{
    repository_id = 1
    code = @"
def calculate(x, y):
    result = x + y
    return result
"@
    language = "python"
    file_path = "calculator.py"
} | ConvertTo-Json

curl -X POST "http://localhost:8000/api/v1/review/analyze" `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d $reviewBody
```

#### 5.3 Check Review Status
```powershell
curl -H "Authorization: Bearer $token" `
  "http://localhost:8000/api/v1/review/{review_id}"
```

#### 5.4 Security Scan
```powershell
$securityBody = @{
    code = @"
api_key = 'sk-1234567890abcdef'
password = 'hardcoded_pass'
"@
    language = "python"
} | ConvertTo-Json

curl -X POST "http://localhost:8000/api/v1/security/scan-secrets" `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d $securityBody
```

### Step 6: Advanced Feature Tests (15 minutes)

#### 6.1 Create Organization
```powershell
$orgBody = @{
    name = "MyCompany"
    description = "My development team"
} | ConvertTo-Json

curl -X POST "http://localhost:8000/api/v1/organizations" `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d $orgBody
```

#### 6.2 List Available Plugins
```powershell
curl -H "Authorization: Bearer $token" `
  "http://localhost:8000/api/v1/plugins"
```

#### 6.3 Enable Plugin
```powershell
curl -X POST "http://localhost:8000/api/v1/plugins/style_checker/enable" `
  -H "Authorization: Bearer $token"
```

#### 6.4 Get Dashboard Analytics
```powershell
curl -H "Authorization: Bearer $token" `
  "http://localhost:8000/api/v1/analytics/dashboard"
```

#### 6.5 WebSocket Test (Real-time Updates)
```javascript
// Open browser console at http://localhost:8000/docs
const ws = new WebSocket('ws://localhost:8000/ws/test-client-123');

ws.onopen = () => {
    console.log('Connected');
    ws.send(JSON.stringify({
        type: 'subscribe',
        channel: 'reviews'
    }));
};

ws.onmessage = (event) => {
    console.log('Message:', JSON.parse(event.data));
};
```

### Step 7: Integration Tests (10 minutes)

#### 7.1 Full PR Review Workflow
```powershell
# 1. Create a test PR payload (simulate GitHub webhook)
$prWebhook = @{
    action = "opened"
    pull_request = @{
        number = 123
        title = "Add new feature"
        html_url = "https://github.com/user/repo/pull/123"
        head = @{
            sha = "abc123"
        }
    }
    repository = @{
        full_name = "username/test-repo"
    }
} | ConvertTo-Json -Depth 5

# 2. Send webhook
curl -X POST "http://localhost:8000/api/v1/webhooks/github" `
  -H "Content-Type: application/json" `
  -H "X-GitHub-Event: pull_request" `
  -d $prWebhook
```

#### 7.2 Run Automated Tests
```powershell
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test categories
pytest tests/test_auth.py -v
pytest tests/test_review_api.py -v
pytest tests/test_security_scanner.py -v
```

### Step 8: Monitoring & Metrics (5 minutes)

#### 8.1 Check Prometheus Metrics
```powershell
curl http://localhost:8000/metrics
```

#### 8.2 View Grafana Dashboard
Open browser: http://localhost:3001 (if using docker-compose)
- Username: admin
- Password: admin

#### 8.3 Check Application Logs
```powershell
# If running locally
Get-Content logs/app.log -Tail 50

# If using Docker
docker-compose logs -f backend
```

---

## 🔍 Troubleshooting Guide

### Issue: Can't connect to GitHub repository
**Solution:**
```powershell
# 1. Verify GitHub token
$env:GITHUB_TOKEN = Get-Content .env | Select-String "GITHUB_TOKEN" | ForEach-Object { ($_ -split '=')[1] }

# 2. Test GitHub API
curl -H "Authorization: token $env:GITHUB_TOKEN" https://api.github.com/user
```

### Issue: OpenAI API errors
**Solution:**
```powershell
# 1. Verify API key
$env:OPENAI_API_KEY = Get-Content .env | Select-String "OPENAI_API_KEY" | ForEach-Object { ($_ -split '=')[1] }

# 2. Test OpenAI API
python -c "from openai import OpenAI; client = OpenAI(); print(client.models.list())"
```

### Issue: Database connection failed
**Solution:**
```powershell
# 1. Check PostgreSQL is running
docker ps | Select-String postgres

# 2. Test connection
python -c "from app.db.database import engine; engine.connect()"
```

### Issue: Why can't I see my personal repositories?
**Solution:**
The application requires:
1. **GitHub Token with correct scopes**: `repo`, `read:org`, `read:user`
2. **OAuth App setup** (optional): For seeing private repos
3. **Repository Registration**: You need to explicitly add repositories via the API

```powershell
# Check token scopes
curl -H "Authorization: token YOUR_GITHUB_TOKEN" `
  https://api.github.com/user/repos?type=all&per_page=100
```

---

## 📊 Feature Coverage Matrix

| Category | Features | Status | Test Command |
|----------|----------|--------|--------------|
| **Auth** | 7 | ✅ | `pytest tests/test_auth.py` |
| **Review API** | 8 | ✅ | `pytest tests/test_review_api.py` |
| **Security** | 4 | ✅ | `pytest tests/test_security_scanner.py` |
| **Analytics** | 4 | ✅ | `pytest tests/test_integration.py` |
| **Plugins** | 4 | ✅ | Manual testing via `/plugins` endpoint |
| **Organizations** | 4 | ✅ | Manual testing via `/organizations` endpoint |
| **WebSocket** | 2 | ✅ | Browser console test |
| **Monitoring** | 3 | ✅ | Check `/metrics` |
| **GitHub** | 5 | ✅ | Webhook simulation |
| **Infrastructure** | 4 | ✅ | `docker-compose up` |

**Total: 45+ Features - All Implemented ✅**

---

## 🎯 Next Steps

1. **Run Full Test Suite**: `pytest tests/ -v --cov=app`
2. **Deploy to Production**: Follow `docs/DEPLOYMENT.md`
3. **Set up Monitoring**: Configure Grafana dashboards
4. **Enable CI/CD**: Push to GitHub to trigger workflows
5. **Add Your Repositories**: Use the repository API to register repos

---

## 📞 Support

- 📖 **Documentation**: See `docs/` folder
- 🐛 **Issues**: Check GitHub Issues
- 💬 **API Docs**: http://localhost:8000/docs
- 📊 **Monitoring**: http://localhost:3001 (Grafana)

**Happy Testing! 🚀**
