# Platform Storage

This directory contains Kubernetes storage configuration for the AWS SRE Observability Platform.

## Purpose

The storage layer validates dynamic EBS volume provisioning through the AWS EBS CSI driver.

## Components

| File | Purpose |
|---|---|
| `gp3-storageclass.yaml` | Defines the default encrypted gp3 StorageClass |
| `ebs-pvc-test.yaml` | Creates a test namespace and PVC |
| `ebs-pod-test.yaml` | Mounts the PVC into a test pod |

## Architecture

```text
Kubernetes PVC
  -> gp3 StorageClass
  -> AWS EBS CSI Driver
  -> AWS EBS Volume
  -> Pod volume mount
```
##Apply
```shell
kubectl apply -f platform/storage/gp3-storageclass.yaml
kubectl apply -f platform/storage/ebs-pvc-test.yaml
kubectl apply -f platform/storage/ebs-pod-test.yaml
```
##Validate
```shell
kubectl get storageclass
kubectl -n storage-test get pod,pvc
kubectl get pv
kubectl -n storage-test logs ebs-gp3-test-pod
```

- Expected pod log:
  - EBS CSI storage test successful 
  - Cleanup 
  - kubectl delete namespace storage-test
  

# EBS CSI Driver IRSA Fix

## Problem

The AWS EBS CSI driver was installed in the EKS cluster, but the controller pods were failing with `CrashLoopBackOff`.

The root error from the `ebs-plugin` container was:

```text
get credentials: failed to refresh cached credentials
no EC2 IMDS role found
```

> This meant the EBS CSI controller pod had no valid AWS IAM credentials. 
> Because the controller was unhealthy, the sidecar containers could not connect to the CSI socket:
```text
/var/lib/csi/sockets/pluginproxy/csi.sock
```


As a result, the EKS managed add-on stayed stuck in:

`CREATING`
##Root Cause

- The EBS CSI driver runs as a Kubernetes workload:

```text
Namespace: kube-system
ServiceAccount: ebs-csi-controller-sa
```

However, it needs AWS permissions to call EC2/EBS APIs such as:

```text
ec2:CreateVolume
ec2:AttachVolume
ec2:DeleteVolume
ec2:DescribeVolumes
ec2:DescribeAvailabilityZones
```

The service account was initially not correctly using IRSA credentials.

The controller pod was missing these required environment variables:

```text
AWS_ROLE_ARN
AWS_WEB_IDENTITY_TOKEN_FILE
```

- Without those, the pod could not assume the IAM role and fell back to EC2 metadata credentials, which were not available.

## Fix Implemented

We implemented the EBS CSI IAM integration using Terraform.

### 1. IAM/OIDC configuration

A dedicated IAM module now creates:

```text
EKS OIDC provider
EBS CSI IAM role
AmazonEBSCSIDriverPolicy attachment
```


The IAM role trusts only this Kubernetes service account:

```text
system:serviceaccount:kube-system:ebs-csi-controller-sa
```

The role is attached to:

```text
arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy
```
###2. EKS add-on configuration

A storage module now manages the EKS managed add-on:

```text
aws-ebs-csi-driver
```

The add-on is configured with:

```text
service_account_role_arn = sre-observability-dev-ebs-csi-driver-role
```

This binds the EBS CSI controller service account to the IAM role.

### 3. Controller pod recreation

> After the service account annotation was added, the existing controller pods still lacked IRSA variables.
> We deleted/restarted the EBS CSI controller pods so new pods could be created with the correct IRSA injection.

After recreation, the ebs-plugin container correctly showed:
```text
AWS_ROLE_ARN=arn:aws:iam::521544431137:role/sre-observability-dev-ebs-csi-driver-role
AWS_WEB_IDENTITY_TOKEN_FILE=/var/run/secrets/eks.amazonaws.com/serviceaccount/token
```
##Final Healthy State

The EBS CSI controller pods became healthy:

```text
ebs-csi-controller-*   6/6   Running
ebs-csi-node-*         3/3   Running
```

The EKS managed add-on became active:

```text
Status = ACTIVE
Version = v1.59.0-eksbuild.1
```

Terraform was also cleaned up:

```text
Resource was untainted
Duplicate module/resource blocks were removed
Invalid variable line was removed
Final plan showed only in-place update
```

Final Terraform plan:

```text
Plan: 0 to add, 1 to change, 0 to destroy
```
##Final Architecture
```text
module.eks
  -> EKS cluster and node group

module.iam
  -> EKS OIDC provider
  -> EBS CSI IRSA role
  -> AmazonEBSCSIDriverPolicy attachment

module.storage
  -> aws-ebs-csi-driver managed add-on
  -> service_account_role_arn binding
```
## Result

> The EBS CSI driver can now securely authenticate to AWS using IRSA and manage EBS volumes for Kubernetes PersistentVolumeClaims.
> This enables dynamic EBS-backed persistent storage for:

```text
Prometheus
Grafana
Loki
PostgreSQL
other stateful workloads
```
