output "eks_oidc_provider_arn" {
  description = "IAM OIDC provider ARN for the EKS cluster"
  value       = aws_iam_openid_connect_provider.eks.arn
}

output "ebs_csi_driver_role_arn" {
  description = "IAM role ARN used by the Amazon EBS CSI Driver"
  value       = aws_iam_role.ebs_csi_driver.arn
}

output "aws_load_balancer_controller_role_arn" {
  description = "IAM role ARN used by the AWS Load Balancer Controller"
  value       = aws_iam_role.aws_load_balancer_controller.arn
}