resource "aws_db_subnet_group" "postgres" {
  name        = "${var.project_name}-postgres"
  description = "Database subnet group for AI SOC PostgreSQL"
  subnet_ids  = module.vpc.database_subnets

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-postgres-subnet-group"
  })
}

resource "aws_db_parameter_group" "postgres" {
  name   = "${var.project_name}-postgres-16"
  family = "postgres16"

  parameter {
    name  = "log_connections"
    value = "1"
  }

  parameter {
    name  = "log_disconnections"
    value = "1"
  }

  parameter {
    name  = "log_checkpoints"
    value = "1"
  }

  parameter {
    name         = "shared_preload_libraries"
    value        = "pg_stat_statements"
    apply_method = "pending-reboot"
  }

  parameter {
    name  = "pg_stat_statements.track"
    value = "all"
  }

  parameter {
    name  = "log_min_duration_statement"
    value = "1000"
  }

  tags = local.common_tags
}

resource "aws_rds_cluster" "postgres" {
  cluster_identifier = "${var.project_name}-postgres"

  engine         = "aurora-postgresql"
  engine_version = "16.3"
  database_name  = "aisoc"
  master_username = "aisoc"
  master_password = var.postgres_password

  db_subnet_group_name   = aws_db_subnet_group.postgres.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  db_cluster_parameter_group_name = aws_db_parameter_group.postgres.name

  storage_encrypted     = true
  deletion_protection   = var.environment == "production"
  skip_final_snapshot   = var.environment != "production"
  final_snapshot_identifier = var.environment == "production" ? "${var.project_name}-postgres-final" : null

  backup_retention_period      = var.environment == "production" ? 14 : 7
  preferred_backup_window      = "03:00-04:00"
  preferred_maintenance_window = "sun:04:00-sun:05:00"

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-postgres-cluster"
  })
}

resource "aws_rds_cluster_instance" "postgres" {
  count = var.environment == "production" ? 2 : 1

  identifier         = "${var.project_name}-postgres-${count.index}"
  cluster_identifier = aws_rds_cluster.postgres.id
  instance_class     = var.postgres_instance_class

  engine         = aws_rds_cluster.postgres.engine
  engine_version = aws_rds_cluster.postgres.engine_version

  publicly_accessible    = false
  db_parameter_group_name = aws_db_parameter_group.postgres.name

  performance_insights_enabled    = true
  performance_insights_kms_key_id = aws_kms_key.rds.arn
  performance_insights_retention_period = 7

  monitoring_interval = 60
  monitoring_role_arn = aws_iam_role.rds_monitoring.arn

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-postgres-instance-${count.index}"
  })
}

resource "aws_kms_key" "rds" {
  description             = "KMS key for RDS encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-rds-kms"
  })
}

resource "aws_iam_role" "rds_monitoring" {
  name = "${var.project_name}-rds-monitoring"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "monitoring.rds.amazonaws.com"
      }
    }]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  role       = aws_iam_role.rds_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}
