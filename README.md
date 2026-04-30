# AWS SRE Observability Platform

## Overview

This project builds a production-style **Site Reliability Engineering (SRE) and Observability Platform** on **AWS EKS** for a realistic banking-style microservices workload.

The workload is based on **Bank of Anthos**, but the main focus of this project is **not application development**. The application is used as a realistic fintech workload to generate traffic, service dependencies, logs, metrics, traces, failures, and operational signals.

The real goal is to design, deploy, observe, troubleshoot, and operate the platform like an SRE team would in a cloud-native financial technology environment.

---

## Project Goal

The goal is to build an AWS/EKS observability platform that can answer critical reliability questions:

- Is the banking workload available?
- Are users experiencing high latency?
- Are backend services failing?
- Are databases healthy?
- Are pods restarting, pending, or being evicted?
- Are logs being collected and searchable?
- Are distributed traces available for request investigation?
- Are alerts actionable?
- Are SLOs defined and measurable?
- Can incidents be diagnosed and recovered quickly?

---

## High-Level Architecture Flow

```text
Developer / Git Repository
        |
        v
Terraform
        |
        v
AWS Infrastructure
        |
        +--> VPC
        +--> Public / Private Subnets
        +--> EKS Cluster
        +--> Managed Node Groups
        +--> IAM / IRSA
        +--> EBS CSI Driver
        +--> AWS Load Balancer Controller
        |
        v
Amazon EKS
        |
        +--> fintech-workload namespace
        |       |
        |       +--> Bank of Anthos workload
        |       +--> frontend
        |       +--> userservice
        |       +--> contacts
        |       +--> balancereader
        |       +--> transactionhistory
        |       +--> ledgerwriter
        |       +--> accounts-db
        |       +--> ledger-db
        |       +--> loadgenerator
        |
        +--> monitoring namespace
        |       |
        |       +--> Prometheus
        |       +--> Grafana
        |       +--> Alertmanager
        |       +--> kube-state-metrics
        |       +--> node-exporter
        |
        +--> logging namespace
        |       |
        |       +--> OpenSearch
        |       +--> Fluent Bit / Log Shipper
        |
        +--> tracing namespace
                |
                +--> OpenTelemetry Collector
                +--> Jaeger / Tempo
```