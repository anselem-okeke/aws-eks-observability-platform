# Bank of Anthos Workload SLIs and SLOs

## Purpose

This document defines the initial workload-level SLIs and SLOs for the Bank of Anthos application.

These SLOs focus on application availability, workload stability, database health, and ingress availability.

## Scope

Workload SLOs cover:

- Pod availability
- Deployment availability
- Stateful database availability
- Pod restart stability
- Ingress availability

Namespace:

```text
fintech-workload
```
###SLO 1: Workload Pod Availability
###SLI

Number of pods not running.

PromQL
```text
sum(kube_pod_status_phase{
  namespace="fintech-workload",
  phase=~"Pending|Failed|Unknown"
})
```
###SLO Target
```text
No Bank of Anthos pod should remain Pending, Failed, or Unknown for more than 5 minutes.
```
###Alert
```text
BankOfAnthosPodNotRunning
```
###SLO 2: Deployment Availability
###SLI

Unavailable replicas for Bank of Anthos deployments.

PromQL
```text
kube_deployment_status_replicas_unavailable{
  namespace="fintech-workload"
}
```
###SLO Target
```text
All Bank of Anthos deployments should have zero unavailable replicas during normal operation.
```
###Alert
```text
BankOfAnthosDeploymentUnavailable
```
###SLO 3: Stateful Database Availability
###SLI

Ready replicas compared to desired replicas for database StatefulSets.

PromQL
```text
kube_statefulset_status_replicas_ready{
  namespace="fintech-workload"
}
<
kube_statefulset_replicas{
  namespace="fintech-workload"
}
```
###SLO Target
```text
Database StatefulSets should have all desired replicas ready.
```
###Alert
```text
BankOfAnthosStatefulSetUnavailable
```
###SLO 4: Pod Restart Stability
###SLI

Pod restart count over 15 minutes.

PromQL
```text
sum by (pod) (
  increase(kube_pod_container_status_restarts_total{
    namespace="fintech-workload"
  }[15m])
)
```
###SLO Target
```text
No Bank of Anthos pod should restart unexpectedly within a 15-minute window.
```
###Alert
```text
BankOfAnthosPodRestarting
```
###SLO 5: Ingress Availability
###SLI

Presence of the Bank of Anthos frontend ingress.

PromQL
```text
count(kube_ingress_info{
  namespace="fintech-workload",
  ingress="bank-of-anthos-frontend"
})
```
###SLO Target
```text
The Bank of Anthos frontend ingress should exist and be discoverable by Prometheus.
```
###Alert
```text
BankOfAnthosIngressMissing
```
###Future Application-Level SLOs

These will be added after application metrics, logs, and tracing are onboarded:

- Frontend HTTP success rate
- Frontend p95 latency
- Backend dependency error rate
- Database query latency
- End-to-end transaction success rate