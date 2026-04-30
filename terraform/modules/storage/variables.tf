variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
}

variable "ebs_csi_driver_role_arn" {
  description = "IAM role ARN used by the Amazon EBS CSI Driver add-on"
  type        = string
}

variable "node_group_name" {
  description = "EKS node group name. Used to order add-on creation after worker nodes."
  type        = string
}

variable "environment" {
  description = "Environment name, for example dev, stage, prod"
  type        = string
}

variable "project_name" {
  description = "Project name used for tagging"
  type        = string
}

