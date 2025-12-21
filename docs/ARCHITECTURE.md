# Architecture Documentation

## System Overview

AI-Powered Code Reviewer is an enterprise-grade code review automation platform that uses AI to analyze code quality, detect security issues, and provide actionable feedback.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │   Web    │  │  Mobile  │  │   CLI    │  │   IDE    │       │
│  │   App    │  │   App    │  │   Tool   │  │  Plugin  │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
└───────┼────────────┼─────────────┼─────────────┼──────────────┘
        │            │             │             │
        └────────────┴─────────────┴─────────────┘
                           │
        ┌──────────────────▼───────────────────┐
        │     Load Balancer / Ingress          │
        │        (Nginx / ALB)                 │
        └──────────────────┬───────────────────┘
                           │
        ┌──────────────────▼───────────────────┐
        │         API Gateway Layer            │
        │   ┌───────────────────────────┐      │
        │   │  Rate Limiting            │      │
        │   │  Authentication (JWT)     │      │
        │   │  Request Validation       │      │
        │   └───────────────────────────┘      │
        └──────────────────┬───────────────────┘
                           │
        ┌──────────────────▼───────────────────────────────────┐
        │              Application Layer                       │
        │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
        │  │   FastAPI    │  │   WebSocket  │  │   Auth    │ │
        │  │   Backend    │  │   Service    │  │  Service  │ │
        │  └──────┬───────┘  └──────┬───────┘  └─────┬─────┘ │
        └─────────┼──────────────────┼─────────────────┼───────┘
                  │                  │                 │
        ┌─────────▼──────────────────▼─────────────────▼───────┐
        │              Service Layer                            │
        │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐│
        │  │   Code   │ │    AI    │ │ Security │ │  GitHub ││
        │  │ Analyzer │ │ Service  │ │ Scanner  │ │ Service ││
        │  └──────────┘ └──────────┘ └──────────┘ └─────────┘│
        └───────────────────────────┬─────────────────────────┘
                                    │
        ┌───────────────────────────▼─────────────────────────┐
        │           Async Processing Layer                     │
        │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
        │  │    Celery    │  │    Celery    │  │   Redis   │ │
        │  │   Workers    │  │     Beat     │  │   Queue   │ │
        │  └──────────────┘  └──────────────┘  └───────────┘ │
        └──────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────▼─────────────────────────┐
        │             Data Layer                               │
        │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
        │  │  PostgreSQL  │  │    Redis     │  │  ChromaDB │ │
        │  │   Database   │  │    Cache     │  │  Vector   │ │
        │  └──────────────┘  └──────────────┘  └───────────┘ │
        └──────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────▼─────────────────────────┐
        │          External Services                           │
        │  ┌──────────┐ ┌──────────┐ ┌──────────┐            │
        │  │ OpenAI   │ │  GitHub  │ │ Gemini   │            │
        │  │   API    │ │   API    │ │   API    │            │
        │  └──────────┘ └──────────┘ └──────────┘            │
        └──────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────▼─────────────────────────┐
        │        Observability Layer                           │
        │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
        │  │  Prometheus  │  │   Grafana    │  │  Logs     │ │
        │  │   Metrics    │  │  Dashboard   │  │  (Cloud)  │ │
        │  └──────────────┘  └──────────────┘  └───────────┘ │
        └──────────────────────────────────────────────────────┘
```

## Component Descriptions

### 1. Client Layer
- **Web App**: Next.js frontend with React
- **Mobile App**: React Native (future)
- **CLI Tool**: Python CLI for CI/CD integration
- **IDE Plugin**: VS Code extension

### 2. API Gateway
- **Load Balancer**: Nginx or AWS ALB
- **Rate Limiting**: Redis-based sliding window
- **Authentication**: JWT tokens with refresh mechanism
- **CORS**: Configurable origins

### 3. Application Layer
- **FastAPI Backend**: Async Python web framework
- **WebSocket Service**: Real-time updates for code reviews
- **Auth Service**: User management, OAuth2, API keys
- **Plugin System**: Extensible analyzer architecture

### 4. Service Layer
- **Code Analyzer**: Static analysis, complexity metrics
- **AI Service**: OpenAI GPT-4 + Google Gemini integration
- **Security Scanner**: Vulnerability detection, secrets scanning
- **GitHub Service**: Webhook handling, PR automation

### 5. Async Processing
- **Celery Workers**: Background task processing
- **Celery Beat**: Scheduled tasks (cleanup, reports)
- **Redis Queue**: Message broker for Celery

### 6. Data Layer
- **PostgreSQL**: Primary database (reviews, users, audits)
- **Redis**: Caching + rate limiting + session storage
- **ChromaDB**: Vector database for RAG (code embeddings)

### 7. External Services
- **OpenAI API**: GPT-4 for code review generation
- **Google Gemini**: Alternative AI model
- **GitHub API**: Repository access, webhooks

### 8. Observability
- **Prometheus**: Metrics collection (15+ custom metrics)
- **Grafana**: Visualization dashboards
- **CloudWatch/Stackdriver**: Centralized logging

## Data Flow

### Code Review Flow
1. User triggers review via webhook/API
2. Request authenticated via JWT
3. Code fetched from GitHub
4. Celery task queued for async processing
5. Code Analyzer runs static analysis
6. Security Scanner checks for vulnerabilities
7. AI Service generates review using GPT-4
8. Results cached in Redis
9. Stored in PostgreSQL
10. WebSocket broadcasts real-time updates
11. Final results returned to user

### Authentication Flow
1. User submits credentials
2. Password verified using bcrypt
3. JWT access token generated (15min expiry)
4. Refresh token issued (7 day expiry)
5. Tokens stored in httpOnly cookies
6. Subsequent requests include JWT in header
7. Middleware validates token signature
8. User context injected into request

## Scalability

### Horizontal Scaling
- **Backend**: Stateless containers (2-10 replicas)
- **Celery Workers**: Auto-scale based on queue length
- **Database**: Read replicas for analytics
- **Redis**: Cluster mode for high availability

### Performance Optimizations
- Response caching (Redis)
- Database query optimization
- Connection pooling
- Async I/O throughout
- CDN for static assets

## Security

### Defense in Depth
1. **Network**: VPC, security groups, TLS 1.3
2. **Application**: Input validation, CSRF tokens, rate limiting
3. **Data**: Encryption at rest and in transit
4. **Access**: RBAC, API keys, OAuth2
5. **Monitoring**: Audit logs, anomaly detection

### Compliance
- PCI-DSS considerations
- GDPR data handling
- SOC 2 controls
- HIPAA-ready architecture

## Deployment

### Container Orchestration
- **Development**: Docker Compose
- **Production**: Kubernetes (EKS/GKE/AKS)
- **Serverless**: AWS Fargate

### Infrastructure as Code
- **Terraform**: AWS/GCP/Azure provisioning
- **Kubernetes**: Declarative manifests
- **CI/CD**: GitHub Actions

## Disaster Recovery

### Backup Strategy
- **Database**: Daily automated backups (7-day retention)
- **Code**: Git version control
- **Configuration**: Infrastructure as Code

### High Availability
- **Multi-AZ deployment**: 99.95% uptime SLA
- **Failover**: Automatic database promotion
- **Load balancing**: Health check-based routing

## Technology Stack Summary

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS |
| Backend | FastAPI 0.104, Python 3.10+, Pydantic v2 |
| Database | PostgreSQL 15, Redis 7, ChromaDB 0.4 |
| Queue | Celery 5.3, Redis broker |
| AI/ML | OpenAI GPT-4, Google Gemini, LangChain |
| Auth | JWT (python-jose), OAuth2, bcrypt |
| Monitoring | Prometheus, Grafana |
| Deployment | Docker, Kubernetes, Terraform |
| CI/CD | GitHub Actions, CodeQL |
