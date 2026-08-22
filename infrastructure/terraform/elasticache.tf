resource "aws_elasticache_subnet_group" "redis" {
  name       = "${var.project_name}-redis"
  subnet_ids = module.vpc.database_subnets

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-redis-subnet-group"
  })
}

resource "aws_elasticache_replication_group" "redis" {
  replication_group_id = "${var.project_name}-redis"
  description          = "Redis cluster for AI SOC Platform"

  node_type            = var.redis_node_type
  num_cache_clusters   = var.redis_num_cache_nodes
  port                 = 6379

  subnet_group_name  = aws_elasticache_subnet_group.redis.name
  security_group_ids = [aws_security_group.redis.id]

  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token                = var.redis_password

  automatic_failover_enabled = var.environment == "production"
  multi_az_enabled           = var.environment == "production"

  snapshot_retention_limit = var.environment == "production" ? 7 : 1
  snapshot_window          = "03:00-05:00"
  maintenance_window       = "sun:05:00-sun:07:00"

  engine         = "redis"
  engine_version = "7.1"
  family         = "redis7"

  parameter_group_name = "default.redis7"

  log_delivery_configuration {
    destination      = aws_cloudwatch_log_group.redis_slow.name
    destination_type = "cloudwatch-logs"
    log_format       = "text"
    log_type         = "slow-log"
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-redis"
  })
}

resource "aws_cloudwatch_log_group" "redis_slow" {
  name              = "/aws/elasticache/${var.project_name}-redis/slow-log"
  retention_in_days = 14

  tags = local.common_tags
}
