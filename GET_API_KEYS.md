# How to Get API Keys and Tokens

This guide will walk you through getting all the necessary API keys and tokens for the AI-Powered Code & PR Review System.

## Required Tokens

You need at least these:
1. **GitHub Personal Access Token** (required for analyzing PRs)
2. **OpenAI API Key** OR **Google Gemini API Key** (required for AI analysis)

## 1. GitHub Personal Access Token

### Step-by-Step Instructions:

1. **Go to GitHub Settings**
   - Visit: https://github.com/settings/tokens
   - Or navigate: Click your profile picture → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Generate New Token**
   - Click "Generate new token" → "Generate new token (classic)"
   - You may need to confirm your password

3. **Configure Token**
   - **Note**: `AI Code Review System`
   - **Expiration**: Choose 90 days or No expiration (not recommended for production)
   - **Select Scopes** (check these boxes):
     - ✅ `repo` - Full control of private repositories
       - This includes: `repo:status`, `repo_deployment`, `public_repo`, `repo:invite`, `security_events`
     - ✅ `read:org` - Read org and team membership, read org projects
     - ✅ `read:user` - Read user profile data
     - ✅ `user:email` - Access user email addresses

4. **Generate and Copy**
   - Click "Generate token" at the bottom
   - **IMPORTANT**: Copy the token immediately - you won't be able to see it again!
   - The token starts with `ghp_`

5. **Add to .env File**
   - Open your `.env` file
   - Replace `your_github_token_here` with your actual token:
   ```
   GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### Example Token:
```
GITHUB_TOKEN=ghp_1234567890abcdefghijklmnopqrstuvwxyz123456
```

---

## 2. OpenAI API Key (Option 1 - Recommended)

### Step-by-Step Instructions:

1. **Create OpenAI Account**
   - Go to: https://platform.openai.com/signup
   - Sign up with email or continue with Google/Microsoft

2. **Add Payment Method** (Required)
   - Go to: https://platform.openai.com/account/billing/overview
   - Click "Add payment method"
   - Add credit card (even $5 credit is enough to start)
   - **Note**: OpenAI requires prepaid credits

3. **Get API Key**
   - Go to: https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Give it a name: `Code Review System`
   - Click "Create secret key"
   - **IMPORTANT**: Copy the key immediately - you can't see it again!
   - The key starts with `sk-`

4. **Add to .env File**
   - Open your `.env` file
   - Replace `your_openai_api_key_here` with your actual key:
   ```
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
   - Make sure `AI_PROVIDER=openai`

### Example Key:
```
OPENAI_API_KEY=sk-proj-1234567890abcdefghijklmnopqrstuvwxyz123456789012
AI_PROVIDER=openai
```

### Cost Estimation:
- **GPT-4 Turbo**: ~$0.01 per 1K input tokens, ~$0.03 per 1K output tokens
- **Average PR Analysis**: $0.05 - $0.20 per review
- **$5 credit**: ~25-100 PR reviews

---

## 3. Google Gemini API Key (Option 2 - Alternative to OpenAI)

If you prefer to use Google Gemini instead of OpenAI (it's free with limits!):

### Step-by-Step Instructions:

1. **Get Gemini API Key**
   - Go to: https://makersuite.google.com/app/apikey
   - Sign in with your Google account
   - Click "Create API key"
   - Select "Create API key in new project" or choose existing project
   - Copy the API key

2. **Add to .env File**
   - Open your `.env` file
   - Uncomment the Gemini lines and add your key:
   ```
   GEMINI_API_KEY=your_actual_gemini_key_here
   GEMINI_MODEL=gemini-pro
   AI_PROVIDER=gemini
   ```
   - Comment out or remove OpenAI lines

### Example Configuration:
```
# Use Gemini instead of OpenAI
GEMINI_API_KEY=AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GEMINI_MODEL=gemini-pro
AI_PROVIDER=gemini
```

### Gemini Advantages:
- ✅ **Free tier** with generous limits
- ✅ 60 requests per minute
- ✅ Good performance for code analysis
- ❌ Less consistent than GPT-4

---

## Final .env File Example

Here's what your complete `.env` file should look like:

```env
# GitHub Configuration
GITHUB_TOKEN=ghp_1234567890abcdefghijklmnopqrstuvwxyz123456

# OpenAI Configuration (if using OpenAI)
OPENAI_API_KEY=sk-proj-1234567890abcdefghijklmnopqrstuvwxyz123456789012
OPENAI_MODEL=gpt-4-turbo-preview
AI_PROVIDER=openai

# OR Google Gemini Configuration (if using Gemini instead)
# GEMINI_API_KEY=AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# GEMINI_MODEL=gemini-pro
# AI_PROVIDER=gemini

# Vector Database Configuration
CHROMA_PERSIST_DIRECTORY=./data/chroma
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Application Configuration
APP_NAME=AI Code Review System
APP_VERSION=1.0.0
DEBUG=True
LOG_LEVEL=INFO
MAX_WORKERS=4

# Review Configuration
MAX_FILE_SIZE_MB=5
SUPPORTED_LANGUAGES=python,javascript,typescript,java,go,rust,cpp,csharp,ruby,php
COMPLEXITY_THRESHOLD=10
SECURITY_SCAN_ENABLED=True

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

---

## Verification Steps

After adding your tokens, verify they work:

### 1. Test Configuration
```powershell
python -c "from app.core.config import settings; print('GitHub Token:', 'Set' if settings.GITHUB_TOKEN else 'Not Set'); print('AI Provider:', settings.AI_PROVIDER); print('AI Key:', 'Set' if (settings.OPENAI_API_KEY or settings.GEMINI_API_KEY) else 'Not Set')"
```

### 2. Initialize Knowledge Base
```powershell
python -m app.scripts.init_knowledge_base
```

Should output:
```
INFO - Starting knowledge base initialization
INFO - Loading knowledge base from: ./app/knowledge_base
INFO - Successfully loaded 165 documents
```

### 3. Start the Server
```powershell
uvicorn app.main:app --reload
```

### 4. Check Health
Visit: http://localhost:8000/api/v1/health/

Should show:
```json
{
  "status": "healthy",
  "services": {
    "github": "configured",
    "ai_provider": "openai_configured"
  }
}
```

---

## Troubleshooting

### "Invalid GitHub Token"
- Verify the token has `repo` scope
- Check token hasn't expired
- Ensure there are no extra spaces in .env file

### "OpenAI Authentication Error"
- Verify you've added payment method
- Check you have available credits
- Ensure API key is correct (starts with `sk-`)

### "Gemini API Error"
- Verify you're in a supported country
- Check API is enabled in Google Cloud Console
- Ensure you haven't hit rate limits

### "Configuration Not Loading"
- Ensure `.env` file is in project root directory
- Restart any running servers after changing .env
- Check for syntax errors in .env (no quotes needed)

---

## Security Best Practices

⚠️ **NEVER commit your .env file to Git!**

The `.gitignore` file already includes `.env`, but double-check:

```bash
# Verify .env is ignored
git status
# Should NOT show .env file
```

### Additional Security:
1. Use separate tokens for development and production
2. Rotate tokens every 90 days
3. Use minimal required scopes
4. Never share tokens in screenshots or logs
5. Revoke tokens immediately if compromised

---

## Cost Management

### OpenAI Cost Tips:
1. Start with $5-10 credit
2. Set up billing alerts
3. Use `gpt-3.5-turbo` for testing (cheaper)
4. Monitor usage: https://platform.openai.com/usage

### Gemini Advantages:
- Free tier includes 60 requests/minute
- Good for development and testing
- Switch to OpenAI for production if needed

---

## Quick Reference

| Service | URL | Starts With | Cost |
|---------|-----|-------------|------|
| GitHub Token | https://github.com/settings/tokens | `ghp_` | Free |
| OpenAI Key | https://platform.openai.com/api-keys | `sk-` | Paid |
| Gemini Key | https://makersuite.google.com/app/apikey | `AIza` | Free* |

*Free tier with limits

---

## Next Steps

Once you have your tokens configured:

1. ✅ Run knowledge base initialization
2. ✅ Start the API server
3. ✅ Test with a sample PR analysis
4. ✅ Read API_EXAMPLES.md for usage examples

Need help? Check the QUICKSTART.md or README.md files!
