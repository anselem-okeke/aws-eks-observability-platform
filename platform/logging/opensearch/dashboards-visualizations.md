# OpenSearch Dashboards Visualizations

## Dashboard Name

Kubernetes Log Observability Baseline

## Purpose

This dashboard provides Kubernetes log visibility for workload and platform troubleshooting.

It helps answer:

- Are logs being ingested into OpenSearch?
- Which namespace is producing the most logs?
- Which container or pod is noisy?
- Are error logs increasing?
- Are application logs visible?
- Are platform components such as AWS Load Balancer Controller, EBS CSI, and Fluent Bit producing useful diagnostic logs?

## Data Source

OpenSearch index pattern / data view:

```text
kubernetes-logs*
```
Time field:
```text
@timestamp
```
##Saved Searches

| Saved Search                      | Purpose                                  |
| --------------------------------- | ---------------------------------------- |
| Bank of Anthos Logs               | Application logs from `fintech-workload` |
| Kube System Controller Logs       | Kubernetes platform/controller logs      |
| Error Investigation Logs          | Error-focused investigation view         |
| AWS Load Balancer Controller Logs | ALB/Ingress troubleshooting              |
| EBS CSI Logs                      | PVC/EBS volume troubleshooting           |
| Fluent Bit Pipeline Logs          | Logging pipeline troubleshooting         |

##Dashboard Rows
###Row 1 — Log Overview
| Panel                | Type       | Purpose                                      |
| -------------------- | ---------- | -------------------------------------------- |
| Total Logs Over Time | Line chart | Shows overall log ingestion rate             |
| Logs by Namespace    | Bar chart  | Shows which namespace produces the most logs |
| Logs by Container    | Bar chart  | Shows noisy containers                       |
###Row 2 — Error Visibility
| Panel                    | Type         | Query                                                                | Purpose                                   |
| ------------------------ | ------------ | -------------------------------------------------------------------- | ----------------------------------------- |
| Error Logs Over Time     | Line chart   | `log: ("error" OR "failed" OR "exception" OR "timeout" OR "denied")` | Shows error trend over time               |
| Error Logs by Namespace  | Bar chart    | Same error query                                                     | Shows which namespace produces error logs |
| Error Investigation Logs | Saved search | Same error query                                                     | Shows actual error log lines              |
###Row 3 — Workload Logs
| Panel                         | Type         | Filter                                          | Purpose                       |
| ----------------------------- | ------------ | ----------------------------------------------- | ----------------------------- |
| Bank of Anthos Logs Over Time | Line chart   | `kubernetes.namespace_name: "fintech-workload"` | Shows workload log activity   |
| Bank of Anthos Logs by Pod    | Bar chart    | `kubernetes.namespace_name: "fintech-workload"` | Shows noisy application pods  |
| Bank of Anthos Logs           | Saved search | `kubernetes.namespace_name: "fintech-workload"` | Shows recent application logs |
###Row 4 — Platform Logs
| Panel                                  | Type         | Purpose                                                         |
| -------------------------------------- | ------------ | --------------------------------------------------------------- |
| AWS Load Balancer Controller Log Count | Metric       | Shows ALB controller log activity                               |
| EBS CSI Errors by Container            | Bar chart    | Shows which EBS CSI sidecar is producing storage-related errors |
| AWS Load Balancer Controller Logs      | Saved search | Shows ALB controller diagnostic logs                            |
| Fluent Bit Pipeline Logs               | Saved search | Shows logging pipeline activity                                 |
##Interpretation Guide
###Total Logs Over Time
| Signal          | Meaning                                                                  |
| --------------- | ------------------------------------------------------------------------ |
| Steady log flow | Log ingestion is healthy                                                 |
| Sudden spike    | Possible retry loop, deployment event, traffic spike, or noisy component |
| Drop to zero    | Fluent Bit, OpenSearch, or workload logging issue                        |
##Logs by Namespace
| Signal                       | Meaning                                       |
| ---------------------------- | --------------------------------------------- |
| `fintech-workload` dominates | Application workload is the main log producer |
| `kube-system` dominates      | Platform components are producing most logs   |
| `logging` dominates          | Logging pipeline may be noisy                 |
| Namespace disappears         | Possible workload or log collection issue     |
##Logs by Container
| Signal                                   | Meaning                                   |
| ---------------------------------------- | ----------------------------------------- |
| One container dominates                  | Investigate noisy workload/component      |
| `fluent-bit` dominates                   | Logging pipeline may be retrying or noisy |
| `aws-load-balancer-controller` dominates | Check ALB/Ingress reconciliation          |
| CSI containers dominate                  | Check PVC/EBS/storage behavior            |
##Error Logs
| Severity | Condition                            |
| -------- | ------------------------------------ |
| Green    | 0 error logs                         |
| Warning  | More than 5 error logs in 5 minutes  |
| Critical | More than 20 error logs in 5 minutes |

##EBS CSI Errors

> If csi-snapshotter dominates, it usually indicates snapshot-related watch/list errors, often caused by missing VolumeSnapshot CRDs.

- Common messages:

```text
failed to list *v1.VolumeSnapshotContent
failed to list *v1.VolumeSnapshotClass
```

- This does not necessarily block normal PVC provisioning unless snapshot functionality is required.

##Fluent Bit Pipeline Logs

Use this panel to check:

```text
OpenSearch connection errors
Retry loops
Dropped records
Parser errors
Buffer issues
File tailing activity

```
##AWS Load Balancer Controller Logs
Use this panel to check:

```text
Ingress reconciliation
ALB creation
Target group registration
IAM/IRSA permission errors
Subnet discovery issues
Security group issues
```
##Investigation Flow
```text
Grafana alert fires
  -> Identify affected namespace/pod
  -> Open OpenSearch Dashboards
  -> Check Total Logs Over Time
  -> Check Logs by Namespace / Container
  -> Check Error Logs Over Time
  -> Open relevant saved search
  -> Filter by namespace, pod, or container
  -> Compare with Kubernetes events
  -> Update runbook or alert rule
```

