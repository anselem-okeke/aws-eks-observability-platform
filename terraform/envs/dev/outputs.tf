output "vpc_id" {
  description = "VPC ID."
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "Public subnet IDs."
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "Private subnet IDs."
  value       = module.vpc.private_subnet_ids
}

output "cluster_name" {
  description = "EKS cluster name."
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "EKS cluster endpoint."
  value       = module.eks.cluster_endpoint
}

output "cluster_security_group_id" {
  description = "EKS cluster security group ID."
  value       = module.eks.cluster_security_group_id
}

output "ebs_csi_driver_role_arn" {
  description = "IAM role ARN used by the Amazon EBS CSI Driver"
  value       = module.iam.ebs_csi_driver_role_arn
}

output "eks_oidc_provider_arn" {
  description = "IAM OIDC provider ARN for the EKS cluster"
  value       = module.iam.eks_oidc_provider_arn
}

output "ebs_csi_addon_name" {
  description = "EKS add-on name for Amazon EBS CSI Driver"
  value       = module.storage.ebs_csi_addon_name
}

output "aws_load_balancer_controller_role_arn" {
  description = "IAM role ARN for AWS Load Balancer Controller"
  value       = module.iam.aws_load_balancer_controller_role_arn
}
