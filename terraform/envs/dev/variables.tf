variable "aws_region" {
  description = "AWS region used for the dev environment."
  type        = string
  default     = "eu-central-1"
}

variable "project_name" {
  description = "Project name used for naming AWS resources."
  type        = string
  default     = "sre-observability"
}

variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "CIDR block for the project VPC."
  type        = string
  default     = "10.40.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones for the VPC."
  type        = list(string)
  default     = ["eu-central-1a", "eu-central-1b"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets."
  type        = list(string)
  default     = ["10.40.0.0/24", "10.40.1.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets."
  type        = list(string)
  default     = ["10.40.10.0/24", "10.40.11.0/24"]
}

variable "cluster_name" {
  description = "EKS cluster name."
  type        = string
  default     = "sre-observability-dev"
}

variable "kubernetes_version" {
  description = "EKS Kubernetes version."
  type        = string
  default     = "1.33"
}

variable "node_instance_types" {
  description = "EC2 instance types for the EKS managed node group."
  type        = list(string)
  default     = ["t3.medium"]
}

variable "node_desired_size" {
  description = "Desired number of worker nodes."
  type        = number
  default     = 2
}

variable "node_min_size" {
  description = "Minimum number of worker nodes."
  type        = number
  default     = 2
}

variable "node_max_size" {
  description = "Maximum number of worker nodes."
  type        = number
  default     = 3
}

variable "tags" {
  description = "Default tags applied to AWS resources."
  type        = map(string)

  default = {
    Project     = "aws-sre-observability-platform"
    Environment = "dev"
    ManagedBy   = "terraform"
    Owner       = "anselem"
  }
}
