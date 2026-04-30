variable "project_name" {
  description = "Project name used for resource naming."
  type        = string
}

variable "environment" {
  description = "Deployment environment."
  type        = string
}

variable "cluster_name" {
  description = "EKS cluster name."
  type        = string
}

variable "kubernetes_version" {
  description = "EKS Kubernetes version."
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs used by the EKS cluster and node group."
  type        = list(string)
}

variable "node_instance_types" {
  description = "Instance types for the EKS managed node group."
  type        = list(string)
}

variable "node_desired_size" {
  description = "Desired node group size."
  type        = number
}

variable "node_min_size" {
  description = "Minimum node group size."
  type        = number
}

variable "node_max_size" {
  description = "Maximum node group size."
  type        = number
}
