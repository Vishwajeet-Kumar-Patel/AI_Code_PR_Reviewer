# Terraform Infrastructure

Infrastructure as Code for deploying AI Code Reviewer to cloud platforms.

## Supported Providers

- AWS (Amazon Web Services)
- GCP (Google Cloud Platform)
- Azure (Microsoft Azure)

## Quick Start

```bash
cd terraform/aws  # or gcp, azure

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -var-file="production.tfvars"

# Apply infrastructure
terraform apply -var-file="production.tfvars"

# Destroy infrastructure
terraform destroy -var-file="production.tfvars"
```

## Architecture

### AWS
- ECS Fargate for container orchestration
- RDS PostgreSQL for database
- ElastiCache Redis for caching
- Application Load Balancer
- CloudWatch for monitoring
- S3 for static assets

### GCP
- Cloud Run for containers
- Cloud SQL PostgreSQL
- Memorystore Redis
- Cloud Load Balancing
- Cloud Monitoring
- Cloud Storage

### Azure
- Container Instances
- Azure Database for PostgreSQL
- Azure Cache for Redis
- Application Gateway
- Azure Monitor
- Blob Storage

## Variables

Create a `production.tfvars` file:

```hcl
project_name = "ai-code-reviewer"
environment = "production"
region = "us-east-1"  # or your preferred region

database_password = "your-secure-password"
redis_password = "your-redis-password"
jwt_secret = "your-jwt-secret"

container_image = "your-registry/ai-code-reviewer:latest"
```

## Outputs

After deployment, Terraform will output:
- Load balancer URL
- Database endpoint
- Redis endpoint
- Monitoring dashboard URLs
