# -----------------------------------------------------------------------------
# Amazon EBS CSI Driver EKS Managed Add-on
# -----------------------------------------------------------------------------

resource "aws_eks_addon" "aws_ebs_csi_driver" {
  cluster_name = var.cluster_name
  addon_name   = "aws-ebs-csi-driver"

  service_account_role_arn = var.ebs_csi_driver_role_arn

  resolve_conflicts_on_create = "OVERWRITE"
  resolve_conflicts_on_update = "OVERWRITE"

  timeouts {
    create = "40m"
    update = "40m"
    delete = "30m"
  }

  tags = {
    Name        = "${var.cluster_name}-aws-ebs-csi-driver"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "terraform"
  }
}