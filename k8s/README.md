# Kubernetes Deployment

Production-grade Kubernetes manifests for AI Code Reviewer.

## Prerequisites

- Kubernetes cluster (1.24+)
- kubectl configured
- Helm 3.x (optional)
- Persistent Volume provisioner
- Ingress controller (nginx recommended)

## Quick Deploy

```bash
# Create namespace
kubectl apply -f namespace.yaml

# Create secrets
kubectl create secret generic app-secrets \
  --from-literal=database-url='postgresql://user:pass@host:5432/db' \
  --from-literal=redis-url='redis://host:6379' \
  --from-literal=jwt-secret='your-secret' \
  -n ai-code-reviewer

# Deploy PostgreSQL
kubectl apply -f postgres.yaml

# Deploy Redis
kubectl apply -f redis.yaml

# Deploy application
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml

# Deploy monitoring
kubectl apply -f prometheus.yaml
kubectl apply -f grafana.yaml
```

## Architecture

- **Backend Deployment**: 3 replicas with HPA
- **Celery Workers**: 2 replicas for async tasks
- **PostgreSQL**: StatefulSet with persistent storage
- **Redis**: StatefulSet for caching/queuing
- **Nginx Ingress**: TLS termination
- **Prometheus**: Metrics collection
- **Grafana**: Visualization

## Scaling

```bash
# Manual scaling
kubectl scale deployment backend -n ai-code-reviewer --replicas=5

# Horizontal Pod Autoscaler is configured for:
# - Min: 2 replicas
# - Max: 10 replicas
# - Target: 70% CPU
```

## Monitoring

```bash
# Check pod status
kubectl get pods -n ai-code-reviewer

# View logs
kubectl logs -f deployment/backend -n ai-code-reviewer

# Port forward to Grafana
kubectl port-forward svc/grafana 3000:3000 -n ai-code-reviewer
```

## Updating

```bash
# Update image
kubectl set image deployment/backend \
  backend=your-registry/ai-code-reviewer:v2.0.0 \
  -n ai-code-reviewer

# Rolling update status
kubectl rollout status deployment/backend -n ai-code-reviewer

# Rollback if needed
kubectl rollout undo deployment/backend -n ai-code-reviewer
```
