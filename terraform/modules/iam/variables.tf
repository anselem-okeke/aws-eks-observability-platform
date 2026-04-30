variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
}

variable "cluster_oidc_issuer_url" {
  description = "EKS cluster OIDC issuer URL"
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