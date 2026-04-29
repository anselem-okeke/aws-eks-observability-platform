#!/bin/bash

mkdir -p workloads/bank-of-anthos/base
mkdir -p workloads/bank-of-anthos/aws
mkdir -p platform/observability/kube-prometheus-stack
mkdir -p platform/logging/opensearch
mkdir -p platform/logging/fluent-bit
mkdir -p platform/tracing/opentelemetry
mkdir -p platform/ingress/aws-load-balancer-controller
mkdir -p terraform/envs/dev
mkdir -p terraform/modules/vpc
mkdir -p terraform/modules/eks
mkdir -p terraform/modules/iam
mkdir -p terraform/modules/ecr
mkdir -p terraform/modules/storage
mkdir -p dashboards/platform-health
mkdir -p dashboards/application-sre
mkdir -p dashboards/slo
mkdir -p runbooks
mkdir -p docs
mkdir -p scripts

cp /mnt/data/bank-of-anthos/kubernetes-manifests/*.yaml workloads/bank-of-anthos/base/
cp /mnt/data/bank-of-anthos/extras/jwt/jwt-secret.yaml workloads/bank-of-anthos/base/
