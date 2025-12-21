variable "project_name" {
  description = "Project name"
  type        = string
  default     = "ai-code-reviewer"
}

variable "environment" {
  description = "Environment (dev, staging, production)"
  type        = string
  default     = "production"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "database_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "redis_password" {
  description = "Redis password"
  type        = string
  sensitive   = true
  default     = ""
}

variable "container_image" {
  description = "Docker image for the application"
  type        = string
}

variable "certificate_arn" {
  description = "ARN of SSL certificate"
  type        = string
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "redis_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.micro"
}

variable "task_cpu" {
  description = "ECS task CPU units"
  type        = string
  default     = "256"
}

variable "task_memory" {
  description = "ECS task memory (MB)"
  type        = string
  default     = "512"
}

variable "task_count" {
  description = "Number of ECS tasks"
  type        = number
  default     = 2
}
