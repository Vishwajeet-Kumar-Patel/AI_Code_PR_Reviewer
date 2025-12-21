# API Documentation

## Base URL
```
Production: https://api.ai-code-reviewer.com
Development: http://localhost:8000
```

## Authentication

All API requests require authentication using JWT tokens.

### Get Access Token
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "SecurePassword123!"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### Using Tokens
Include the access token in the Authorization header:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## Endpoints

### Health Check
```http
GET /api/v1/health

Response:
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Code Review

#### Create Review
```http
POST /api/v1/reviews
Authorization: Bearer <token>
Content-Type: application/json

{
  "repository_url": "https://github.com/user/repo",
  "pr_number": 123,
  "focus_areas": ["security", "performance"]
}

Response:
{
  "review_id": "rev_abc123",
  "status": "processing",
  "estimated_time": 120
}
```

#### Get Review Status
```http
GET /api/v1/reviews/{review_id}
Authorization: Bearer <token>

Response:
{
  "review_id": "rev_abc123",
  "status": "completed",
  "quality_score": 85,
  "findings": [
    {
      "type": "security",
      "severity": "high",
      "file": "app/main.py",
      "line": 42,
      "message": "SQL injection vulnerability detected"
    }
  ],
  "summary": "Overall code quality is good...",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### WebSocket

#### Connect to Real-time Updates
```javascript
const ws = new WebSocket(
  'wss://api.ai-code-reviewer.com/api/v1/ws/reviews?token=<jwt_token>'
);

ws.onopen = () => {
  // Subscribe to review updates
  ws.send(JSON.stringify({
    type: 'subscribe',
    review_id: 'rev_abc123'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data);
};
```

### Analytics

#### Dashboard Statistics
```http
GET /api/v1/analytics/dashboard?time_range=7d
Authorization: Bearer <token>

Response:
{
  "total_reviews": 150,
  "average_quality_score": 82.5,
  "reviews_by_status": {
    "completed": 140,
    "processing": 8,
    "failed": 2
  },
  "top_issues": [
    {"issue": "Missing error handling", "count": 23},
    {"issue": "Unused imports", "count": 18}
  ]
}
```

### Security Scanning

#### Scan for Secrets
```http
POST /api/v1/security/scan/secrets
Authorization: Bearer <token>
Content-Type: application/json

{
  "code": "api_key = 'AKIA1234567890ABCDEF'",
  "file_path": "config.py"
}

Response:
{
  "total_secrets": 1,
  "findings": [
    {
      "type": "secret",
      "secret_type": "aws_access_key",
      "severity": "critical",
      "line": 1,
      "recommendation": "Use AWS IAM roles or Secrets Manager"
    }
  ]
}
```

### Organizations

#### Create Organization
```http
POST /api/v1/organizations
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Acme Corp",
  "slug": "acme-corp",
  "plan": "pro"
}

Response:
{
  "organization": {
    "id": 1,
    "name": "Acme Corp",
    "slug": "acme-corp",
    "plan": "pro"
  }
}
```

### Plugins

#### List Plugins
```http
GET /api/v1/plugins
Authorization: Bearer <token>

Response:
{
  "plugins": [
    {
      "name": "StyleCheckerPlugin",
      "version": "1.0.0",
      "enabled": true,
      "supported_languages": ["python", "javascript"]
    }
  ]
}
```

## Rate Limits

| Tier | Requests/Minute | Burst |
|------|----------------|-------|
| Free | 10 | 20 |
| Pro | 100 | 200 |
| Enterprise | 1000 | 2000 |

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

## Error Responses

```json
{
  "detail": "Error message",
  "status_code": 400,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Common Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Too Many Requests
- `500` - Internal Server Error

## SDKs

### Python
```python
from ai_code_reviewer import Client

client = Client(api_key="your_api_key")
review = client.create_review(
    repository_url="https://github.com/user/repo",
    pr_number=123
)
```

### JavaScript/TypeScript
```typescript
import { AICodeReviewer } from '@ai-code-reviewer/sdk';

const client = new AICodeReviewer({ apiKey: 'your_api_key' });
const review = await client.createReview({
  repositoryUrl: 'https://github.com/user/repo',
  prNumber: 123
});
```

## Webhooks

Configure webhooks to receive notifications:

```json
{
  "event": "review.completed",
  "review_id": "rev_abc123",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "quality_score": 85,
    "findings_count": 12
  }
}
```

Events:
- `review.started`
- `review.completed`
- `review.failed`
- `security.issue_found`
