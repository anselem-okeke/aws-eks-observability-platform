# Dev Terraform Environment

This environment provisions the development AWS infrastructure for the SRE observability platform.

## Components

- VPC
- public subnets
- private subnets
- internet gateway
- public route table
- EKS cluster
- EKS managed node group

## Cost-Aware Design

This first dev version runs EKS worker nodes in public subnets to avoid NAT Gateway costs.

Production improvement:

- move worker nodes to private subnets
- add NAT Gateway or VPC endpoints
- restrict API access
- use private endpoint access
- add stricter security groups

## Usage

```bash
cd terraform/envs/dev

terraform init
terraform fmt -recursive
terraform validate
terraform plan
terraform apply
```
## Configure kubectl
```shell
aws eks update-kubeconfig \
  --region eu-central-1 \
  --name sre-observability-dev
```
## Destroy
```shell
terraform destroy
```