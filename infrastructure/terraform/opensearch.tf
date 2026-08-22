resource "aws_opensearch_domain" "soc" {
  domain_name    = "${var.project_name}-opensearch"
  engine_version = "OpenSearch_2.12"

  cluster_config {
    instance_type            = var.opensearch_instance_type
    instance_count           = var.opensearch_instance_count
    dedicated_master_enabled = var.opensearch_instance_count >= 3
    dedicated_master_type    = "m6g.large.search"
    dedicated_master_count   = 3
    zone_awareness_enabled   = true
    zone_awareness_config {
      availability_zone_count = 2
    }
  }

  ebs_options {
    ebs_enabled = true
    volume_type = "gp3"
    volume_size = var.opensearch_volume_size
  }

  vpc_options {
    subnet_ids         = slice(module.vpc.database_subnets, 0, 2)
    security_group_ids = [aws_security_group.opensearch.id]
  }

  encrypt_at_rest {
    enabled    = true
    kms_key_id = aws_kms_key.opensearch.arn
  }

  node_to_node_encryption {
    enabled = true
  }

  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }

  log_publishing_options {
    cloudwatch_log_group_arn = "${aws_cloudwatch_log_group.opensearch_index.arn}:*"
    log_type                 = "INDEX_SLOW_LOGS"
  }

  log_publishing_options {
    cloudwatch_log_group_arn = "${aws_cloudwatch_log_group.opensearch_index.arn}:*"
    log_type                 = "SEARCH_SLOW_LOGS"
  }

  log_publishing_options {
    cloudwatch_log_group_arn = "${aws_cloudwatch_log_group.opensearch_index.arn}:*"
    log_type                 = "ES_APPLICATION_LOGS"
  }

  access_policies = data.aws_iam_policy_document.opensearch.json

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-opensearch"
  })
}

data "aws_iam_policy_document" "opensearch" {
  statement {
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
    actions   = ["es:*"]
    resources = ["${aws_opensearch_domain.soc.arn}/*"]
    condition {
      test     = "IpAddress"
      variable = "aws:SourceIp"
      values   = ["10.0.0.0/8"]
    }
  }
}

resource "aws_kms_key" "opensearch" {
  description             = "KMS key for OpenSearch encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-opensearch-kms"
  })
}

resource "aws_cloudwatch_log_group" "opensearch_index" {
  name              = "/opensearch/${var.project_name}/index"
  retention_in_days = 30

  tags = local.common_tags
}

resource "aws_iam_role" "opensearch_cloudwatch" {
  name = "${var.project_name}-opensearch-cloudwatch"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "es.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "opensearch_cloudwatch" {
  role       = aws_iam_role.opensearch_cloudwatch.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}
