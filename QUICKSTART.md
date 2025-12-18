# Quick Start Guide

Get your AI-Powered Code & PR Review System up and running in minutes!

## Prerequisites

- Python 3.10 or higher
- Git
- GitHub Personal Access Token
- OpenAI API Key or Google Gemini API Key

## Installation Steps

### 1. Clone or Navigate to the Project

```bash
cd "AI_Powered Code & PR Reviewer"
```

### 2. Create Virtual Environment

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file:

```bash
copy .env.example .env   # Windows
cp .env.example .env     # Linux/Mac
```

Edit `.env` and add your credentials:

```bash
# Required
GITHUB_TOKEN=ghp_your_github_token_here
OPENAI_API_KEY=sk-your_openai_key_here

# OR use Gemini instead of OpenAI
# AI_PROVIDER=gemini
# GEMINI_API_KEY=your_gemini_key_here
```

### 5. Initialize Knowledge Base

```bash
python -m app.scripts.init_knowledge_base
```

Expected output:
```
INFO - Starting knowledge base initialization
INFO - Loading knowledge base from: ./app/knowledge_base
INFO - Loaded 45 sections from python.md
INFO - Loaded 52 sections from javascript.md
INFO - Loaded 68 sections from security.md
INFO - Successfully loaded 165 documents
INFO - Knowledge base initialization complete!
```

### 6. Start the Server

```bash
uvicorn app.main:app --reload
```

Or run directly:
```bash
python app/main.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 7. Verify Installation

Open your browser and go to:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health/

Or use curl:
```bash
curl http://localhost:8000/api/v1/health/
```

## Your First PR Analysis

### Method 1: Using Swagger UI

1. Open http://localhost:8000/docs
2. Find the `/api/v1/review/analyze` endpoint
3. Click "Try it out"
4. Enter:
   ```json
   {
     "repository": "octocat/Hello-World",
     "pr_number": 1,
     "include_security_scan": true,
     "include_complexity_analysis": true
   }
   ```
5. Click "Execute"

### Method 2: Using curl

```bash
curl -X POST "http://localhost:8000/api/v1/review/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "repository": "owner/repo-name",
    "pr_number": 123,
    "include_security_scan": true,
    "include_complexity_analysis": true
  }'
```

### Method 3: Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/review/analyze",
    json={
        "repository": "owner/repo-name",
        "pr_number": 123,
        "include_security_scan": True,
        "include_complexity_analysis": True
    }
)

result = response.json()
print(f"Review ID: {result['review_id']}")
print(f"Status: {result['status']}")
if result['status'] == 'completed':
    print(f"Quality Score: {result['summary']['overall_quality_score']}")
```

## Getting Your GitHub Token

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Select scopes:
   - `repo` (Full control of private repositories)
   - `read:org` (Read org and team membership)
4. Copy the token and add it to your `.env` file

## Getting Your OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key and add it to your `.env` file
4. Make sure you have credits in your account

## Getting Your Gemini API Key (Alternative)

1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API key"
3. Copy the key and add it to your `.env` file
4. Update `AI_PROVIDER=gemini` in your `.env`

## Testing the System

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_complexity_analyzer.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Test Individual Components

**Test Language Detection:**
```python
from app.utils.language_detector import LanguageDetector

detector = LanguageDetector()
print(detector.detect("script.py"))  # Output: python
print(detector.detect("app.ts"))     # Output: typescript
```

**Test Complexity Analysis:**
```python
from app.services.complexity_analyzer import ComplexityAnalyzer

analyzer = ComplexityAnalyzer()
code = """
def hello():
    print("Hello, World!")
    return True
"""
metrics = analyzer.analyze(code, "python", "test.py")
print(f"Cyclomatic Complexity: {metrics.cyclomatic_complexity}")
print(f"Maintainability Index: {metrics.maintainability_index}")
```

**Test Security Scanner:**
```python
from app.services.security_scanner import SecurityScanner

scanner = SecurityScanner()
code = 'password = "secret123"'
findings = scanner.scan(code, "python", "test.py")
print(f"Found {len(findings)} security issues")
```

## Troubleshooting

### Port Already in Use

If port 8000 is already in use, specify a different port:
```bash
uvicorn app.main:app --port 8080 --reload
```

### GitHub Token Issues

If you get authentication errors:
1. Verify token has correct permissions
2. Check token hasn't expired
3. Ensure `.env` file is in the project root
4. Restart the server after updating `.env`

### OpenAI API Errors

If you get OpenAI API errors:
1. Verify API key is correct
2. Check you have available credits
3. Ensure you're not hitting rate limits
4. Try switching to Gemini as an alternative

### Vector Database Issues

If ChromaDB initialization fails:
```bash
# Clear the database and reinitialize
rm -rf data/chroma    # Linux/Mac
rmdir /s data\chroma  # Windows

# Reinitialize
python -m app.scripts.init_knowledge_base
```

### Module Not Found Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Or install individually
pip install fastapi uvicorn pydantic python-dotenv
pip install pygithub openai google-generativeai
pip install chromadb sentence-transformers langchain
```

## Next Steps

1. **Customize Knowledge Base**: Add your own best practices to `app/knowledge_base/best_practices/`

2. **Set Up GitHub Webhooks**: Automate PR reviews by configuring webhooks

3. **Configure for Production**: See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment

4. **Explore API**: Check out [API_EXAMPLES.md](API_EXAMPLES.md) for more examples

5. **Contribute**: Add support for more languages and security patterns

## Common Use Cases

### Analyze All Open PRs in a Repository

```python
import requests

# Get all open PRs (you'll need to implement this endpoint or use GitHub API)
# Then analyze each one

def analyze_all_prs(repository):
    # Fetch open PRs using GitHub API
    # For each PR:
    response = requests.post(
        "http://localhost:8000/api/v1/review/analyze",
        json={
            "repository": repository,
            "pr_number": pr_number
        }
    )
    return response.json()
```

### Integrate with CI/CD

Add to your GitHub Actions workflow:

```yaml
name: Code Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - name: Run AI Code Review
        run: |
          curl -X POST "${{ secrets.CODE_REVIEW_API }}/api/v1/review/analyze" \
            -H "Content-Type: application/json" \
            -d "{\"repository\": \"${{ github.repository }}\", \"pr_number\": ${{ github.event.pull_request.number }}}"
```

### Schedule Regular Reviews

```python
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()

@scheduler.scheduled_job('cron', hour=9, minute=0)
def daily_review():
    # Analyze recent PRs
    pass

scheduler.start()
```

## Support

- **Documentation**: Check README.md for detailed information
- **API Reference**: http://localhost:8000/docs
- **Issues**: Report bugs and request features via GitHub Issues

## Configuration Options

Key settings in `.env`:

```bash
# Adjust complexity threshold
COMPLEXITY_THRESHOLD=10

# Change supported languages
SUPPORTED_LANGUAGES=python,javascript,typescript,java,go

# Adjust rate limiting
RATE_LIMIT_PER_MINUTE=60

# Change AI model
OPENAI_MODEL=gpt-4-turbo-preview
# or
GEMINI_MODEL=gemini-pro

# Enable debug mode
DEBUG=True
LOG_LEVEL=DEBUG
```

## Performance Tips

1. **Use Redis for caching** (optional but recommended for production)
2. **Adjust MAX_WORKERS** based on your CPU cores
3. **Limit file size** with MAX_FILE_SIZE_MB
4. **Use a more powerful AI model** for better analysis
5. **Pre-load knowledge base** during initialization

Congratulations! You now have a fully functional AI-Powered Code & PR Review System! 🎉
