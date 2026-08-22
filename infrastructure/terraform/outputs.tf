output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = module.vpc.private_subnets
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = module.vpc.public_subnets
}

output "database_subnet_ids" {
  description = "Database subnet IDs"
  value       = module.vpc.database_subnets
}

output "eks_cluster_endpoint" {
  description = "EKS cluster API endpoint"
  value       = module.eks.cluster_endpoint
}

output "eks_cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "eks_cluster_ca_certificate" {
  description = "EKS cluster CA certificate (base64)"
  value       = module.eks.cluster_certificate_authority_data
  sensitive   = true
}

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = aws_db_instance.postgres.endpoint
}

output "rds_port" {
  description = "RDS PostgreSQL port"
  value       = aws_db_instance.postgres.port
}

output "rds_database_name" {
  description = "RDS database name"
  value       = aws_db_instance.postgres.db_name
}

output "elasticache_endpoint" {
  description = "ElastiCache Redis primary endpoint"
  value       = aws_elasticache_cluster.redis.cache_nodes[0].address
}

output "elasticache_port" {
  description = "ElastiCache Redis port"
  value       = aws_elasticache_cluster.redis.cache_nodes[0].port
}

output "msk_bootstrap_brokers" {
  description = "MSK Kafka bootstrap brokers"
  value       = aws_msk_cluster.kafka.bootstrap_brokers
}

output "opensearch_endpoint" {
  description = "OpenSearch domain endpoint"
  value       = aws_opensearch_domain.soc.endpoint
}

output "opensearch_kibana_endpoint" {
  description = "OpenSearch Dashboards endpoint"
  value       = aws_opensearch_domain.soc.kibana_endpoint
}

output "s3_log_bucket_arn" {
  description = "S3 log bucket ARN"
  value       = aws_s3_bucket.logs.arn
}

output "s3_data_bucket_arn" {
  description = "S3 data bucket ARN"
  value       = aws_s3_bucket.data.arn
}

output "s3_models_bucket_arn" {
  description = "S3 ML models bucket ARN"
  value       = aws_s3_bucket.ml_models.arn
}

output "oidc_provider_arn" {
  description = "OIDC provider ARN for IRSA"
  value       = module.eks.oidc_provider_arn
}
