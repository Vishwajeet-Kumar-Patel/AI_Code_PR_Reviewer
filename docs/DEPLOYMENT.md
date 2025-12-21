# Deployment Guide

## Prerequisites

- Docker 24+ & Docker Compose v2
- Kubernetes 1.24+ (for K8s deployment)
- Terraform 1.0+ (for cloud deployment)
- PostgreSQL 15+
- Redis 7+

## Local Development

### Using Docker Compose

```bash
# Clone repository
git clone https://github.com/yourorg/ai-code-reviewer.git
cd ai-code-reviewer

# Copy environment file
cp .env.example .env

# Edit .env with your API keys
nano .env

# Start services
docker-compose up -d

# Run database migrations
docker-compose exec backend alembic upgrade head

# Create initial user
docker-compose exec backend python -m app.scripts.create_admin

# Access the application
open http://localhost:3000
```

### Manual Setup

```bash
# Backend
cd ai-code-reviewer
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Database setup
createdb codereview
alembic upgrade head

# Start backend
uvicorn app.main:app --reload --port 8000

# Start Celery worker (separate terminal)
celery -A app.workers.celery_app worker --loglevel=info

# Frontend
cd frontend
npm install
npm run dev
```

## Production Deployment

### Option 1: Kubernetes

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secrets
kubectl create secret generic app-secrets \
  --from-literal=database-url='postgresql://user:pass@host:5432/db' \
  --from-literal=redis-url='redis://host:6379' \
  --from-literal=jwt-secret='your-secret' \
  --from-literal=openai-api-key='sk-...' \
  -n ai-code-reviewer

# Deploy infrastructure
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml

# Deploy application
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml

# Verify deployment
kubectl get pods -n ai-code-reviewer
kubectl logs -f deployment/backend -n ai-code-reviewer
```

### Option 2: AWS with Terraform

```bash
cd terraform/aws

# Initialize Terraform
terraform init

# Create tfvars file
cat > production.tfvars <<EOF
project_name = "ai-code-reviewer"
environment = "production"
aws_region = "us-east-1"
container_image = "your-registry/ai-code-reviewer:latest"
database_password = "secure-password"
certificate_arn = "arn:aws:acm:..."
EOF

# Plan deployment
terraform plan -var-file="production.tfvars"

# Apply infrastructure
terraform apply -var-file="production.tfvars"

# Get outputs
terraform output
```

### Option 3: Docker Compose (Production)

```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale backend=3 --scale celery_worker=2
```

## Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1

# Show current version
alembic current
```

## Environment Variables

### Required
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Redis
REDIS_URL=redis://host:6379/0

# Authentication
JWT_SECRET=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=15

# AI Services
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# GitHub
GITHUB_CLIENT_ID=your-client-id
GITHUB_CLIENT_SECRET=your-client-secret
GITHUB_WEBHOOK_SECRET=your-webhook-secret
```

### Optional
```bash
# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG=false

# CORS
CORS_ORIGINS=["https://app.example.com"]

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=100
```

## SSL/TLS Setup

### Let's Encrypt with Cert-Manager

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

## Monitoring Setup

```bash
# Deploy Prometheus
kubectl apply -f k8s/prometheus.yaml

# Deploy Grafana
kubectl apply -f k8s/grafana.yaml

# Access Grafana
kubectl port-forward svc/grafana 3000:3000 -n ai-code-reviewer
# Open http://localhost:3000
# Default: admin/admin
```

## Backup & Restore

### PostgreSQL Backup

```bash
# Backup
kubectl exec -n ai-code-reviewer postgres-0 -- \
  pg_dump -U postgres codereview > backup.sql

# Restore
kubectl exec -i -n ai-code-reviewer postgres-0 -- \
  psql -U postgres codereview < backup.sql
```

### Redis Backup

```bash
# Backup
kubectl exec -n ai-code-reviewer redis-0 -- redis-cli SAVE
kubectl cp ai-code-reviewer/redis-0:/data/dump.rdb ./redis-backup.rdb

# Restore
kubectl cp ./redis-backup.rdb ai-code-reviewer/redis-0:/data/dump.rdb
kubectl rollout restart statefulset/redis -n ai-code-reviewer
```

## Scaling

### Horizontal Pod Autoscaling
```bash
# Already configured in hpa.yaml
# Monitor autoscaling
kubectl get hpa -n ai-code-reviewer

# Manual scaling
kubectl scale deployment backend --replicas=5 -n ai-code-reviewer
```

### Vertical Scaling
```bash
# Update resource limits in deployment.yaml
kubectl apply -f k8s/deployment.yaml
kubectl rollout status deployment/backend -n ai-code-reviewer
```

## Health Checks

```bash
# Backend health
curl https://api.example.com/api/v1/health

# Kubernetes health
kubectl get pods -n ai-code-reviewer
kubectl describe pod <pod-name> -n ai-code-reviewer

# Database connectivity
kubectl exec -it postgres-0 -n ai-code-reviewer -- psql -U postgres -c "SELECT 1"
```

## Troubleshooting

### Pods not starting
```bash
kubectl describe pod <pod-name> -n ai-code-reviewer
kubectl logs <pod-name> -n ai-code-reviewer
```

### Database connection issues
```bash
# Test from pod
kubectl exec -it backend-xxx -n ai-code-reviewer -- \
  python -c "from app.db.database import engine; print(engine)"
```

### High memory usage
```bash
kubectl top pods -n ai-code-reviewer
```

## Security Checklist

- [ ] Change all default passwords
- [ ] Use secrets management (Vault/AWS Secrets Manager)
- [ ] Enable network policies
- [ ] Configure RBAC
- [ ] Enable pod security policies
- [ ] Use non-root containers
- [ ] Enable audit logging
- [ ] Set up vulnerability scanning
- [ ] Configure TLS everywhere
- [ ] Implement rate limiting

## Performance Tuning

### Database
```sql
-- Analyze tables
ANALYZE reviews;

-- Add indexes
CREATE INDEX idx_reviews_created_at ON reviews(created_at);
CREATE INDEX idx_reviews_repository_id ON reviews(repository_id);
```

### Redis
```bash
# Configure max memory
redis-cli CONFIG SET maxmemory 2gb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

### Application
- Enable connection pooling
- Increase worker count
- Configure async I/O limits
- Optimize AI API calls
