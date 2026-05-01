# Platform SLIs and SLOs

## Purpose

This document defines the initial platform-level SLIs and SLOs for the AWS SRE Observability Platform.

The platform SLOs focus on the reliability of the shared Kubernetes and observability.

## Scope

Platform SLOs cover:

- EKS node readiness
- Critical platform controllers
- Persistent storage provisioning
- Monitoring stack availability
- Cluster resource saturation

---

### SLO 1: Node Readiness

### SLI

Percentage of Kubernetes nodes in `Ready` state.

### PromQL

```promql
sum(kube_node_status_condition{condition="Ready",status="true"})
/
count(kube_node_status_condition{condition="Ready",status="true"})
```

### SLO Target
```text
100% of nodes should be Ready during normal operation.
```
###Alert
```text
PlatformNodeNotReady
```
###SLO 2: Critical Controller Availability
###SLI

Available replicas for critical platform controllers.

Critical controllers:

EBS CSI Controller
- AWS Load Balancer Controller
- CoreDNS
- Grafana
- Prometheus
- Alertmanager

PromQL Examples
```text
kube_deployment_status_replicas_available{
  namespace="kube-system",
  deployment="ebs-csi-controller"
}


kube_deployment_status_replicas_available{
  namespace="kube-system",
  deployment="aws-load-balancer-controller"
}
```
###SLO Target
```text
Critical platform controllers should have at least 1 available replica 99.9% of the time.
```
Alerts
```text
EBSCSIControllerUnavailable
AWSLoadBalancerControllerUnavailable
MonitoringStackGrafanaUnavailable
```
###SLO 3: PVC Provisioning Health
###SLI

Number of PVCs stuck in `Pending`.

PromQL
```text
kube_persistentvolumeclaim_status_phase{phase="Pending"} == 1
```
###SLO Target
```text
No PVC should remain Pending for more than 5 minutes.
```
###Alert
```text
PlatformPVCStuckPending
```
###SLO 4: Pod Stability
###SLI

Number of pods in CrashLoopBackOff.

PromQL
```text
kube_pod_container_status_waiting_reason{reason="CrashLoopBackOff"} == 1
```
###SLO Target
```text
No critical platform pod should remain in CrashLoopBackOff for more than 5 minutes.
```
###Alert
```text
PlatformPodCrashLooping
```
###SLO 5: Cluster Resource Saturation
###SLI

Cluster CPU and memory usage as percentage of allocatable resources.

CPU PromQL
```text
100 * (
  sum(rate(container_cpu_usage_seconds_total{container!="",pod!=""}[5m]))
  /
  sum(kube_node_status_allocatable{resource="cpu"})
)
```
Memory PromQL
```text
100 * (
  sum(container_memory_working_set_bytes{container!="",pod!=""})
  /
  sum(kube_node_status_allocatable{resource="memory"})
)
```
###SLO Target
```text
Cluster CPU should remain below 80%.
Cluster memory should remain below 85%.
```
###Alerts
```text
PlatformHighClusterCPU
PlatformHighClusterMemory
```
###Initial Error Budget Policy

For this lab platform:

```text
Warning alerts indicate SLO risk.
Critical alerts indicate active SLO breach.
Repeated critical alerts should trigger investigation and runbook updates.
```