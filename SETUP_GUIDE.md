# Full Stack Setup Guide

## Prerequisites

1. **PostgreSQL** - Install from https://www.postgresql.org/download/windows/
2. **Node.js 18+** - Install from https://nodejs.org/
3. **Python 3.11** - Already installed
4. **Git** - For version control

## Step 1: Set up PostgreSQL Database

### Install PostgreSQL

1. Download PostgreSQL 15 installer for Windows
2. Run installer, set password for postgres user
3. Use default port 5432

### Create Database

Open Command Prompt or PowerShell:

```powershell
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE ai_code_review;

# Create user (optional)
CREATE USER ai_reviewer WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ai_code_review TO ai_reviewer;

# Exit
\q
```

Or using pgAdmin GUI:
1. Open pgAdmin
2. Right-click Databases → Create → Database
3. Name: `ai_code_review`

## Step 2: Install Backend Dependencies

```powershell
# Navigate to project root
cd "C:\Users\vishw\OneDrive\Desktop\AI_Powered Code & PR Reviewer"

# Install database dependencies
pip install -r requirements-db.txt

# Verify installation
pip list | Select-String "sqlalchemy|psycopg2|alembic"
```

## Step 3: Update Backend Configuration

The `.env` file already has DATABASE_URL. Update if needed:

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/ai_code_review
```

## Step 4: Initialize Database

```powershell
# Create tables
python -c "from app.db import init_db; init_db()"

# Verify tables were created
# Using psql:
psql -U postgres -d ai_code_review -c "\dt"
```

Expected tables:
- users
- repositories  
- pull_requests
- reviews
- feedback

## Step 5: Start Backend Server

```powershell
# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/v1/health/

## Step 6: Set up Frontend

```powershell
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Or if you prefer pnpm/yarn:
# pnpm install
# yarn install
```

## Step 7: Configure Frontend Environment

The `.env.local` file is already created. Update if needed:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_VERSION=v1
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/ai_code_review
```

## Step 8: Start Frontend Development Server

```powershell
# From frontend directory
npm run dev
```

Frontend will be available at: http://localhost:3000

## Step 9: Test the Application

### Test Backend

1. Visit http://localhost:8000/docs
2. Try the `/api/v1/health/` endpoint
3. Should return: `{"status": "healthy"}`

### Test Frontend

1. Visit http://localhost:3000
2. Should redirect to http://localhost:3000/dashboard
3. You should see the PR Analysis Dashboard

### Test Full Integration

1. Use the "Analyze PR" button in the UI
2. Or use curl/Postman:

```powershell
# Analyze a PR
curl -X POST "http://localhost:8000/api/v1/review/analyze" `
  -H "Content-Type: application/json" `
  -d '{
    "repository_owner": "owner",
    "repository_name": "repo",
    "pull_request_number": 1
  }'
```

## Troubleshooting

### PostgreSQL Connection Error

```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**
1. Verify PostgreSQL is running: `Get-Service -Name postgresql*`
2. Check connection string in `.env`
3. Test connection: `psql -U postgres -d ai_code_review`

### Port Already in Use

```
OSError: [WinError 10048] Only one usage of each socket address
```

**Solution:**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process
taskkill /PID <process_id> /F
```

### npm install fails

**Solution:**
```powershell
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
Remove-Item -Recurse -Force node_modules
npm install
```

### Database tables not created

**Solution:**
```powershell
# Drop and recreate database
psql -U postgres -c "DROP DATABASE IF EXISTS ai_code_review;"
psql -U postgres -c "CREATE DATABASE ai_code_review;"

# Initialize again
python -c "from app.db import init_db; init_db()"
```

## Development Workflow

### Running Both Servers

**Terminal 1 (Backend):**
```powershell
cd "C:\Users\vishw\OneDrive\Desktop\AI_Powered Code & PR Reviewer"
uvicorn app.main:app --reload
```

**Terminal 2 (Frontend):**
```powershell
cd "C:\Users\vishw\OneDrive\Desktop\AI_Powered Code & PR Reviewer\frontend"
npm run dev
```

### Making Changes

- **Backend changes**: Auto-reload enabled with `--reload` flag
- **Frontend changes**: Auto-reload via Next.js hot module replacement
- **Database changes**: Run migrations or drop/recreate tables

## Production Deployment

See [DEPLOYMENT.md](../DEPLOYMENT.md) for production setup instructions.

## Quick Reference

| Component | URL | Command |
|-----------|-----|---------|
| Frontend | http://localhost:3000 | `npm run dev` |
| Backend API | http://localhost:8000 | `uvicorn app.main:app --reload` |
| API Docs | http://localhost:8000/docs | N/A |
| PostgreSQL | localhost:5432 | `psql -U postgres` |
| Database | ai_code_review | N/A |

## Next Steps

1. Configure GitHub OAuth (optional) - See [GET_API_KEYS.md](../GET_API_KEYS.md)
2. Set up webhooks for automatic PR analysis
3. Configure CI/CD pipeline
4. Set up monitoring and logging
5. Deploy to production

## Support

For issues:
1. Check logs: `./logs/app.log` and `./logs/error.log`
2. Check database: `psql -U postgres -d ai_code_review`
3. Check API docs: http://localhost:8000/docs
4. Review [README.md](../README.md) and [QUICKSTART.md](../QUICKSTART.md)
