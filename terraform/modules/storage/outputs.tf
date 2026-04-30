output "ebs_csi_addon_name" {
  description = "EKS add-on name for Amazon EBS CSI Driver"
  value       = aws_eks_addon.aws_ebs_csi_driver.addon_name
}

output "ebs_csi_addon_arn" {
  description = "EKS add-on ARN for Amazon EBS CSI Driver"
  value       = aws_eks_addon.aws_ebs_csi_driver.arn
}