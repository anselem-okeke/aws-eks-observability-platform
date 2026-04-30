module "vpc" {
  source = "../../modules/vpc"

  project_name         = var.project_name
  environment          = var.environment
  vpc_cidr             = var.vpc_cidr
  availability_zones   = var.availability_zones
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  cluster_name         = var.cluster_name
}

module "eks" {
  source = "../../modules/eks"

  project_name        = var.project_name
  environment         = var.environment
  cluster_name        = var.cluster_name
  kubernetes_version  = var.kubernetes_version
  subnet_ids          = module.vpc.public_subnet_ids
  node_instance_types = var.node_instance_types
  node_desired_size   = var.node_desired_size
  node_min_size       = var.node_min_size
  node_max_size       = var.node_max_size

  depends_on = [
    module.vpc
  ]
}

module "iam" {
  source = "../../modules/iam"

  cluster_name            = module.eks.cluster_name
  cluster_oidc_issuer_url = module.eks.cluster_oidc_issuer_url

  environment  = var.environment
  project_name = var.project_name
}

module "storage" {
  source = "../../modules/storage"

  cluster_name            = module.eks.cluster_name
  node_group_name         = module.eks.node_group_name
  ebs_csi_driver_role_arn = module.iam.ebs_csi_driver_role_arn

  environment  = var.environment
  project_name = var.project_name

  depends_on = [
    module.eks,
    module.iam
  ]
}
