# API Examples

This document provides examples of how to use the AI-Powered Code & PR Review System API.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API uses the GitHub token configured in the environment variables. Future versions will support API key authentication for the review endpoints.

## Endpoints

### Health Check

Check if the API is running and properly configured.

**Request:**
```bash
curl http://localhost:8000/api/v1/health/
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "app_name": "AI Code Review System",
  "services": {
    "github": "configured",
    "ai_provider": "openai_configured",
    "vector_db": {
      "status": "operational",
      "documents": 150
    }
  }
}
```

### Analyze Pull Request

Analyze a GitHub pull request for code quality, security, and complexity.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/review/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "repository": "octocat/Hello-World",
    "pr_number": 1,
    "include_security_scan": true,
    "include_complexity_analysis": true
  }'
```

**Response:**
```json
{
  "review_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "repository": "octocat/Hello-World",
  "pr_number": 1,
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:31:30Z",
  "summary": {
    "total_files": 3,
    "total_lines_changed": 150,
    "overall_quality_score": 85.5,
    "critical_issues": 0,
    "high_issues": 2,
    "medium_issues": 5,
    "low_issues": 3,
    "security_findings_count": 1,
    "average_complexity": 6.2,
    "recommendation": "COMMENT",
    "strengths": [
      "High code quality overall",
      "Low code complexity"
    ],
    "weaknesses": [
      "1 security finding"
    ]
  },
  "file_analyses": [
    {
      "file_path": "src/main.py",
      "language": "python",
      "lines_added": 50,
      "lines_removed": 10,
      "complexity": {
        "cyclomatic_complexity": 5,
        "cognitive_complexity": 3,
        "lines_of_code": 45,
        "maintainability_index": 75.5
      },
      "issues": [
        {
          "category": "quality",
          "severity": "medium",
          "title": "Code Quality Issue",
          "description": "Consider extracting this logic into a separate function",
          "file_path": "src/main.py",
          "line_number": 25,
          "suggestion": "Extract method for better maintainability"
        }
      ],
      "security_findings": [],
      "quality_score": 82.0
    }
  ],
  "ai_insights": "This PR demonstrates good coding practices overall..."
}
```

### Get Review Status

Check the status of a review without fetching all details.

**Request:**
```bash
curl http://localhost:8000/api/v1/review/550e8400-e29b-41d4-a716-446655440000/status
```

**Response:**
```json
{
  "review_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "repository": "octocat/Hello-World",
  "pr_number": 1,
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:31:30Z"
}
```

### Get Review Summary

Get only the summary of a completed review.

**Request:**
```bash
curl http://localhost:8000/api/v1/review/550e8400-e29b-41d4-a716-446655440000/summary
```

**Response:**
```json
{
  "review_id": "550e8400-e29b-41d4-a716-446655440000",
  "summary": {
    "total_files": 3,
    "total_lines_changed": 150,
    "overall_quality_score": 85.5,
    "critical_issues": 0,
    "high_issues": 2,
    "medium_issues": 5,
    "low_issues": 3,
    "security_findings_count": 1,
    "average_complexity": 6.2,
    "recommendation": "COMMENT"
  },
  "ai_insights": "Detailed AI-generated insights..."
}
```

### Get Repository Info

Get information about a GitHub repository.

**Request:**
```bash
curl http://localhost:8000/api/v1/repository/octocat/Hello-World
```

**Response:**
```json
{
  "full_name": "octocat/Hello-World",
  "name": "Hello-World",
  "owner": "octocat",
  "description": "My first repository on GitHub!",
  "language": "Python",
  "languages": {
    "Python": 45000,
    "JavaScript": 15000
  },
  "default_branch": "main",
  "is_private": false,
  "url": "https://api.github.com/repos/octocat/Hello-World",
  "clone_url": "https://github.com/octocat/Hello-World.git",
  "stars": 1500,
  "forks": 200
}
```

### Get Pull Request Data

Get detailed information about a specific pull request.

**Request:**
```bash
curl http://localhost:8000/api/v1/repository/octocat/Hello-World/pulls/1
```

**Response:**
```json
{
  "number": 1,
  "title": "Add new feature",
  "description": "This PR adds...",
  "author": "developer",
  "state": "open",
  "base_branch": "main",
  "head_branch": "feature-branch",
  "created_at": "2024-01-15T09:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z",
  "files": [...],
  "commits": [...],
  "comments": [...],
  "additions": 100,
  "deletions": 20,
  "changed_files": 3
}
```

### List All Reviews

Get a list of all reviews in the system.

**Request:**
```bash
curl http://localhost:8000/api/v1/review/
```

**Response:**
```json
{
  "total": 5,
  "reviews": [
    {
      "review_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "completed",
      "repository": "octocat/Hello-World",
      "pr_number": 1,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

## Python Client Example

```python
import requests
import json

class CodeReviewClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def analyze_pr(self, repository, pr_number):
        """Analyze a pull request"""
        url = f"{self.base_url}/api/v1/review/analyze"
        payload = {
            "repository": repository,
            "pr_number": pr_number,
            "include_security_scan": True,
            "include_complexity_analysis": True
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_review(self, review_id):
        """Get review by ID"""
        url = f"{self.base_url}/api/v1/review/{review_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def wait_for_review(self, review_id, timeout=300):
        """Wait for review to complete"""
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status_url = f"{self.base_url}/api/v1/review/{review_id}/status"
            response = requests.get(status_url)
            data = response.json()
            
            if data["status"] == "completed":
                return self.get_review(review_id)
            elif data["status"] == "failed":
                raise Exception("Review failed")
            
            time.sleep(5)
        
        raise TimeoutError("Review timed out")

# Usage
client = CodeReviewClient()

# Start analysis
result = client.analyze_pr("octocat/Hello-World", 1)
review_id = result["review_id"]

print(f"Review started: {review_id}")
print(f"Status: {result['status']}")

if result["status"] == "completed":
    print(f"Quality Score: {result['summary']['overall_quality_score']}")
    print(f"Issues: {result['summary']['high_issues']} high, {result['summary']['medium_issues']} medium")
```

## JavaScript/Node.js Client Example

```javascript
const axios = require('axios');

class CodeReviewClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }
    
    async analyzePR(repository, prNumber) {
        const url = `${this.baseUrl}/api/v1/review/analyze`;
        const payload = {
            repository,
            pr_number: prNumber,
            include_security_scan: true,
            include_complexity_analysis: true
        };
        
        const response = await axios.post(url, payload);
        return response.data;
    }
    
    async getReview(reviewId) {
        const url = `${this.baseUrl}/api/v1/review/${reviewId}`;
        const response = await axios.get(url);
        return response.data;
    }
    
    async waitForReview(reviewId, timeout = 300000) {
        const startTime = Date.now();
        
        while (Date.now() - startTime < timeout) {
            const statusUrl = `${this.baseUrl}/api/v1/review/${reviewId}/status`;
            const response = await axios.get(statusUrl);
            const data = response.data;
            
            if (data.status === 'completed') {
                return await this.getReview(reviewId);
            } else if (data.status === 'failed') {
                throw new Error('Review failed');
            }
            
            await new Promise(resolve => setTimeout(resolve, 5000));
        }
        
        throw new Error('Review timed out');
    }
}

// Usage
(async () => {
    const client = new CodeReviewClient();
    
    try {
        const result = await client.analyzePR('octocat/Hello-World', 1);
        console.log(`Review started: ${result.review_id}`);
        console.log(`Status: ${result.status}`);
        
        if (result.status === 'completed') {
            console.log(`Quality Score: ${result.summary.overall_quality_score}`);
            console.log(`Issues: ${result.summary.high_issues} high, ${result.summary.medium_issues} medium`);
        }
    } catch (error) {
        console.error('Error:', error.message);
    }
})();
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 404 Not Found
```json
{
  "detail": "Review not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "An internal error occurred"
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse. Default limits:
- 60 requests per minute per IP
- 200 requests per day per IP

When rate limit is exceeded:
```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```
