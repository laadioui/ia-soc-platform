resource "aws_msk_cluster" "kafka" {
  cluster_name           = "${var.project_name}-kafka"
  kafka_version          = "3.6.1"
  number_of_broker_nodes = var.kafka_broker_count

  broker_node_group_info {
    instance_type   = var.kafka_instance_type
    storage_info {
      ebs_storage_info {
        volume_size = var.kafka_ebs_volume_size
      }
    }
    client_subnets = module.vpc.private_subnets
    security_groups = [aws_security_group.kafka.id]
  }

  encryption_info {
    encryption_in_transit {
      client_broker = "TLS"
      in_cluster    = true
    }
    encryption_at_rest_kms_key_arn = aws_kms_key.msk.arn
  }

  configuration_info {
    arn      = aws_msk_configuration.kafka.arn
    revision = aws_msk_configuration.kafka.latest_revision
  }

  logging_info {
    broker_logs {
      cloudwatch_logs {
        enabled   = true
        log_group = aws_cloudwatch_log_group.kafka.name
      }
      s3_logs {
        enabled = true
        bucket  = aws_s3_bucket.logs.id
        prefix  = "kafka-logs"
      }
    }
  }

  open_monitoring {
    prometheus {
      jmx_exporter {
        enabled_in_broker = true
      }
      node_exporter {
        enabled_in_broker = true
      }
    }
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-kafka"
  })
}

resource "aws_msk_configuration" "kafka" {
  name              = "${var.project_name}-kafka-config"
  kafka_versions    = ["3.6.1"]

  server_properties = <<PROPERTIES
auto.create.topics.enable=true
default.replication.factor=1
min.insync.replicas=1
num.partitions=6
log.retention.hours=168
log.retention.bytes=1073741824
compression.type=producer
PROPERTIES
}

resource "aws_cloudwatch_log_group" "kafka" {
  name              = "/msk/${var.project_name}-kafka"
  retention_in_days = 14

  tags = local.common_tags
}

resource "aws_kms_key" "msk" {
  description             = "KMS key for MSK encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-msk-kms"
  })
}
