# AWS Load Balancer Controller

This directory contains the Helm values for installing the AWS Load Balancer Controller in the EKS cluster.

## Purpose

The AWS Load Balancer Controller watches Kubernetes Ingress resources and provisions AWS load balancer resources such as:

- Application Load Balancers
- Target Groups
- Listeners
- Security group rules

## Namespace

The controller runs in:

```text
kube-system
```
##Service Account
```text
aws-load-balancer-controller
```

The service account uses IRSA with the IAM role created by Terraform:

```text
sre-observability-dev-aws-load-balancer-controller-role
```
##Install
```shell
helm repo add eks https://aws.github.io/eks-charts
helm repo update eks

ALB_CONTROLLER_ROLE_ARN=$(cd terraform/envs/dev && terraform output -raw aws_load_balancer_controller_role_arn)

helm upgrade --install aws-load-balancer-controller eks/aws-load-balancer-controller \
  --namespace kube-system \
  --version 1.14.0 \
  -f platform/ingress/aws-load-balancer-controller/values.yaml \
  --set serviceAccount.annotations."eks\.amazonaws\.com/role-arn"="$ALB_CONTROLLER_ROLE_ARN"
```


##Validate
```shell
kubectl -n kube-system get deployment aws-load-balancer-controller
kubectl -n kube-system get pods -l app.kubernetes.io/name=aws-load-balancer-controller
kubectl -n kube-system get sa aws-load-balancer-controller -o yaml | grep -A5 annotations
```
##Architecture
```text
Kubernetes Ingress
  -> AWS Load Balancer Controller
  -> AWS Application Load Balancer
  -> Target Group
  -> Kubernetes Service
  -> Application Pods
```

