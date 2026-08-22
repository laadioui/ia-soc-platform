variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "ai-soc-platform"
}

variable "environment" {
  description = "Deployment environment (development, staging, production)"
  type        = string
  default     = "production"

  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be development, staging, or production."
  }
}

variable "cluster_version" {
  description = "Kubernetes version for EKS cluster"
  type        = string
  default     = "1.29"
}

variable "node_instance_types" {
  description = "EC2 instance types for EKS node groups"
  type        = list(string)
  default     = ["m6i.xlarge", "m6i.2xlarge"]
}

variable "node_desired_size" {
  description = "Desired number of worker nodes"
  type        = number
  default     = 3
}

variable "node_min_size" {
  description = "Minimum number of worker nodes"
  type        = number
  default     = 2
}

variable "node_max_size" {
  description = "Maximum number of worker nodes"
  type        = number
  default     = 10
}

variable "gpu_node_instance_types" {
  description = "EC2 instance types for GPU node group"
  type        = list(string)
  default     = ["p3.2xlarge"]
}

variable "gpu_node_desired_size" {
  description = "Desired number of GPU worker nodes"
  type        = number
  default     = 1
}

variable "gpu_node_min_size" {
  description = "Minimum number of GPU worker nodes"
  type        = number
  default     = 0
}

variable "gpu_node_max_size" {
  description = "Maximum number of GPU worker nodes"
  type        = number
  default     = 3
}

variable "postgres_instance_class" {
  description = "RDS instance class for PostgreSQL"
  type        = string
  default     = "db.r6g.xlarge"
}

variable "postgres_allocated_storage" {
  description = "Allocated storage in GB for PostgreSQL"
  type        = number
  default     = 100
}

variable "postgres_max_allocated_storage" {
  description = "Maximum storage in GB for PostgreSQL autoscaling"
  type        = number
  default     = 500
}

variable "postgres_password" {
  description = "Master password for PostgreSQL"
  type        = string
  sensitive   = true
}

variable "redis_node_type" {
  description = "ElastiCache node type for Redis"
  type        = string
  default     = "cache.r6g.large"
}

variable "redis_num_cache_nodes" {
  description = "Number of Redis cache nodes"
  type        = number
  default     = 2
}

variable "redis_password" {
  description = "Auth token for Redis"
  type        = string
  sensitive   = true
}

variable "kafka_instance_type" {
  description = "Kafka broker instance type for MSK"
  type        = string
  default     = "kafka.m5.large"
}

variable "kafka_broker_count" {
  description = "Number of Kafka brokers"
  type        = number
  default     = 3
}

variable "kafka_ebs_volume_size" {
  description = "EBS volume size in GB per Kafka broker"
  type        = number
  default     = 500
}

variable "opensearch_instance_type" {
  description = "OpenSearch instance type"
  type        = string
  default     = "m6g.xlarge.search"
}

variable "opensearch_instance_count" {
  description = "Number of OpenSearch data nodes"
  type        = number
  default     = 2
}

variable "opensearch_volume_size" {
  description = "EBS volume size in GB per OpenSearch node"
  type        = number
  default     = 100
}

variable "opensearch_password" {
  description = "Master password for OpenSearch"
  type        = string
  sensitive   = true
}

variable "route53_zone_name" {
  description = "Route53 hosted zone name"
  type        = string
  default     = "aisoc.example.com"
}

variable "certificate_arn" {
  description = "ACM certificate ARN for HTTPS"
  type        = string
  default     = ""
}

variable "keycloak_admin_password" {
  description = "Keycloak admin password"
  type        = string
  sensitive   = true
}

variable "jwt_secret_key" {
  description = "JWT secret key"
  type        = string
  sensitive   = true
}
