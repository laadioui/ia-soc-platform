resource "aws_security_group" "rds" {
  name_prefix = "${var.project_name}-rds-"
  description = "Security group for RDS PostgreSQL"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description     = "PostgreSQL from EKS"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [module.eks.node_security_group_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-rds-sg"
  })

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group" "redis" {
  name_prefix = "${var.project_name}-redis-"
  description = "Security group for ElastiCache Redis"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description     = "Redis from EKS"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [module.eks.node_security_group_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-redis-sg"
  })

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group" "kafka" {
  name_prefix = "${var.project_name}-kafka-"
  description = "Security group for MSK Kafka"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description     = "Kafka from EKS"
    from_port       = 9092
    to_port         = 9092
    protocol        = "tcp"
    security_groups = [module.eks.node_security_group_id]
  }

  ingress {
    description     = "Kafka TLS from EKS"
    from_port       = 9094
    to_port         = 9094
    protocol        = "tcp"
    security_groups = [module.eks.node_security_group_id]
  }

  ingress {
    description     = "Zookeeper from EKS"
    from_port       = 2181
    to_port         = 2181
    protocol        = "tcp"
    security_groups = [module.eks.node_security_group_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-kafka-sg"
  })

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group" "opensearch" {
  name_prefix = "${var.project_name}-opensearch-"
  description = "Security group for OpenSearch"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description     = "OpenSearch from EKS"
    from_port       = 9200
    to_port         = 9200
    protocol        = "tcp"
    security_groups = [module.eks.node_security_group_id]
  }

  ingress {
    description     = "OpenSearch inter-node"
    from_port       = 9300
    to_port         = 9300
    protocol        = "tcp"
    self            = true
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-opensearch-sg"
  })

  lifecycle {
    create_before_destroy = true
  }
}
