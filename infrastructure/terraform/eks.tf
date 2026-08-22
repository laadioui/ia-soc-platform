data "aws_caller_identity" "current" {}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.8"

  cluster_name    = "${var.project_name}-cluster"
  cluster_version = var.cluster_version

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  cluster_endpoint_public_access  = true
  cluster_endpoint_private_access = true

  enable_cluster_creator_admin_permissions = true

  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
    aws-ebs-csi-driver = {
      most_recent              = true
      service_account_role_arn = module.ebs_csi_irsa.iam_role_arn
    }
  }

  eks_managed_node_groups = {
    general = {
      name            = "${var.project_name}-general"
      instance_types  = var.node_instance_types
      desired_size    = var.node_desired_size
      min_size        = var.node_min_size
      max_size        = var.node_max_size
      capacity_type   = "ON_DEMAND"

      labels = {
        workload = "general"
      }

      tags = merge(local.common_tags, {
        "k8s.io/cluster-autoscaler/enabled"                     = "true"
        "k8s.io/cluster-autoscaler/${var.project_name}-cluster" = "owned"
      })
    }

    gpu = {
      name            = "${var.project_name}-gpu"
      instance_types  = var.gpu_node_instance_types
      desired_size    = var.gpu_node_desired_size
      min_size        = var.gpu_node_min_size
      max_size        = var.gpu_node_max_size
      capacity_type   = "ON_DEMAND"

      labels = {
        workload        = "ai"
        "nvidia.com/gpu" = "true"
      }

      taints = [{
        key    = "nvidia.com/gpu"
        value  = "present"
        effect = "NO_SCHEDULE"
      }]

      tags = local.common_tags
    }
  }

  tags = local.common_tags
}

module "ebs_csi_irsa" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.37"

  role_name             = "${var.project_name}-ebs-csi"
  attach_ebs_csi_policy = true

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:ebs-csi-controller-sa"]
    }
  }

  tags = local.common_tags
}

module "cluster_autoscaler_irsa" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.37"

  role_name                        = "${var.project_name}-cluster-autoscaler"
  attach_cluster_autoscaler_policy = true
  cluster_autoscaler_cluster_names = [module.eks.cluster_name]

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:cluster-autoscaler"]
    }
  }

  tags = local.common_tags
}
