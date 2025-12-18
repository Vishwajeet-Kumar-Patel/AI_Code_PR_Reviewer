# Deployment Guide

This guide explains how to deploy the AI-Powered Code & PR Review System to production.

## Prerequisites

- Python 3.10 or higher
- PostgreSQL or MySQL (for production database)
- Redis (for caching)
- Docker (optional)
- Cloud platform account (AWS, Azure, or GCP)

## Environment Configuration

### 1. Production Environment Variables

Create a `.env.production` file:

```bash
# Application
APP_NAME=AI Code Review System
APP_VERSION=1.0.0
DEBUG=False
LOG_LEVEL=INFO

# GitHub
GITHUB_TOKEN=your_production_github_token
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# AI Provider (use one)
AI_PROVIDER=openai
OPENAI_API_KEY=your_production_openai_key
OPENAI_MODEL=gpt-4-turbo-preview

# OR use Gemini
# AI_PROVIDER=gemini
# GEMINI_API_KEY=your_gemini_key

# Vector Database
CHROMA_PERSIST_DIRECTORY=/var/lib/code-review/chroma
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Redis
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
REDIS_DB=0

# Security
SECRET_KEY=your-secret-key-change-this

# Paths
KNOWLEDGE_BASE_PATH=/app/knowledge_base
LOGS_PATH=/var/log/code-review
DATA_PATH=/var/lib/code-review
```

## Docker Deployment

### 1. Create Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create necessary directories
RUN mkdir -p /var/log/code-review /var/lib/code-review

# Initialize knowledge base
RUN python -m app.scripts.init_knowledge_base

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 2. Create docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GITHUB_TOKEN=${GITHUB_TOKEN}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - REDIS_HOST=redis
    volumes:
      - ./data:/var/lib/code-review
      - ./logs:/var/log/code-review
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped

volumes:
  redis-data:
```

### 3. Build and Run

```bash
# Build image
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

## AWS Deployment

### Using AWS ECS (Elastic Container Service)

1. **Build and push Docker image to ECR:**

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account.dkr.ecr.us-east-1.amazonaws.com

# Build and tag image
docker build -t code-review-system .
docker tag code-review-system:latest your-account.dkr.ecr.us-east-1.amazonaws.com/code-review-system:latest

# Push to ECR
docker push your-account.dkr.ecr.us-east-1.amazonaws.com/code-review-system:latest
```

2. **Create ECS Task Definition:**

```json
{
  "family": "code-review-system",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "app",
      "image": "your-account.dkr.ecr.us-east-1.amazonaws.com/code-review-system:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DEBUG",
          "value": "False"
        }
      ],
      "secrets": [
        {
          "name": "GITHUB_TOKEN",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:github-token"
        },
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:openai-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/code-review-system",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

3. **Create ECS Service with ALB**

### Using AWS Lambda (Serverless)

Deploy using AWS SAM or Serverless Framework for event-driven PR reviews.

## Azure Deployment

### Using Azure Container Instances

```bash
# Create resource group
az group create --name code-review-rg --location eastus

# Create container registry
az acr create --resource-group code-review-rg --name codereviewacr --sku Basic

# Build and push image
az acr build --registry codereviewacr --image code-review-system:latest .

# Deploy container instance
az container create \
  --resource-group code-review-rg \
  --name code-review-app \
  --image codereviewacr.azurecr.io/code-review-system:latest \
  --dns-name-label code-review-system \
  --ports 8000 \
  --environment-variables \
    DEBUG=False \
  --secure-environment-variables \
    GITHUB_TOKEN=$GITHUB_TOKEN \
    OPENAI_API_KEY=$OPENAI_API_KEY
```

## GCP Deployment

### Using Cloud Run

```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/code-review-system

# Deploy to Cloud Run
gcloud run deploy code-review-system \
  --image gcr.io/PROJECT_ID/code-review-system \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DEBUG=False \
  --set-secrets GITHUB_TOKEN=github-token:latest,OPENAI_API_KEY=openai-key:latest
```

## Kubernetes Deployment

### 1. Create Kubernetes Manifests

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: code-review-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: code-review-system
  template:
    metadata:
      labels:
        app: code-review-system
    spec:
      containers:
      - name: app
        image: your-registry/code-review-system:latest
        ports:
        - containerPort: 8000
        env:
        - name: DEBUG
          value: "False"
        envFrom:
        - secretRef:
            name: code-review-secrets
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /api/v1/health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health/ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

**service.yaml:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: code-review-system
spec:
  selector:
    app: code-review-system
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### 2. Deploy to Kubernetes

```bash
# Create namespace
kubectl create namespace code-review

# Create secrets
kubectl create secret generic code-review-secrets \
  --from-literal=GITHUB_TOKEN=$GITHUB_TOKEN \
  --from-literal=OPENAI_API_KEY=$OPENAI_API_KEY \
  -n code-review

# Apply manifests
kubectl apply -f deployment.yaml -n code-review
kubectl apply -f service.yaml -n code-review

# Check status
kubectl get pods -n code-review
kubectl get svc -n code-review
```

## Post-Deployment

### 1. Verify Deployment

```bash
# Health check
curl https://your-domain.com/api/v1/health/

# Test analysis
curl -X POST https://your-domain.com/api/v1/review/analyze \
  -H "Content-Type: application/json" \
  -d '{"repository": "test/repo", "pr_number": 1}'
```

### 2. Set Up Monitoring

- Configure CloudWatch/Azure Monitor/GCP Monitoring
- Set up alerts for errors and performance issues
- Monitor API response times
- Track review completion rates

### 3. Configure GitHub Webhooks

Set up webhooks to automatically trigger reviews:

1. Go to your GitHub repository settings
2. Add webhook with URL: `https://your-domain.com/api/v1/webhooks/github`
3. Select events: Pull requests
4. Add webhook secret

### 4. Set Up SSL/TLS

Use Let's Encrypt with Certbot or cloud provider SSL certificates.

### 5. Enable Auto-scaling

Configure auto-scaling based on CPU/memory usage or request count.

## Security Checklist

- [ ] All secrets stored in secure secret management
- [ ] HTTPS enabled with valid SSL certificate
- [ ] Rate limiting configured
- [ ] Security headers configured
- [ ] API authentication implemented
- [ ] Regular security updates scheduled
- [ ] Backup strategy implemented
- [ ] Monitoring and alerting configured
- [ ] Access logs enabled
- [ ] DDoS protection enabled

## Maintenance

### Regular Tasks

- Update dependencies monthly
- Review and rotate API keys quarterly
- Monitor and optimize performance
- Review logs for errors
- Backup vector database weekly
- Update knowledge base as needed

### Troubleshooting

Check logs:
```bash
# Docker
docker-compose logs -f app

# Kubernetes
kubectl logs -f deployment/code-review-system -n code-review

# Check health
curl http://localhost:8000/api/v1/health/
```
