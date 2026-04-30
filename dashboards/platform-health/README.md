# Platform Observability Baseline Dashboard

## Purpose

This dashboard provides the first platform-level visibility layer for the AWS SRE Observability Platform.

It focuses on Kubernetes infrastructure health before workload-specific observability is added.

## Dashboard Scope

This dashboard covers:

- Node health
- Pod health
- Namespace health
- PVC/storage health
- EBS CSI controller health
- AWS Load Balancer Controller health
- Cluster CPU and memory saturation

---

## Row 1: Cluster Overview

### Panel: Nodes Ready

**Type:** Stat

```promql
sum(kube_node_status_condition{condition="Ready",status="true"})
```
###Panel: Total Pods Running
####Type: Stat

```text
sum(kube_pod_status_phase{phase="Running"})
```
###Panel: Pods Not Running

####Type: Stat / Table

```text
sum(kube_pod_status_phase{phase=~"Pending|Failed|Unknown"})
```
###Panel: Namespaces Count

####Type: Stat

```text
count(kube_namespace_created)
```
##Row 2: Node Resource Saturation
###Panel: Cluster CPU Usage %

####Type: Gauge

````text
100 * (
  sum(rate(container_cpu_usage_seconds_total{container!="",pod!=""}[5m]))
  /
  sum(kube_node_status_allocatable{resource="cpu"})
)
````
###Panel: Cluster Memory Usage %

####Type: Gauge

```text
100 * (
  sum(container_memory_working_set_bytes{container!="",pod!=""})
  /
  sum(kube_node_status_allocatable{resource="memory"})
)
```
###Panel: CPU Usage by Node

####Type: Time series

```text
100 * (
  sum by (node) (rate(container_cpu_usage_seconds_total{container!="",pod!=""}[5m]))
  /
  sum by (node) (kube_node_status_allocatable{resource="cpu"})
)
```
###Panel: Memory Usage by Node

####Type: Time series

```text
100 * (
  sum by (node) (container_memory_working_set_bytes{container!="",pod!=""})
  /
  sum by (node) (kube_node_status_allocatable{resource="memory"})
)
```
##Row 3: Pod Health
###Panel: Pod Restarts by Namespace

####Type: Bar gauge / Table

```text
sum by (namespace) (increase(kube_pod_container_status_restarts_total[15m]))
```
###Panel: CrashLoopBackOff Pods

####Type: Table

```text
kube_pod_container_status_waiting_reason{reason="CrashLoopBackOff"}
```
###Panel: Pending Pods

####Type: Table

```text
kube_pod_status_phase{phase="Pending"} == 1
```
##Row 4: Storage Health
###Panel: PVC Bound

####Type: Stat

```text
sum(kube_persistentvolumeclaim_status_phase{phase="Bound"})
```
###Panel: PVC Pending

####Type: Stat / Table

```text
sum(kube_persistentvolumeclaim_status_phase{phase="Pending"})
```
###Panel: PVC Capacity by Namespace

####Type: Bar gauge

```text
sum by (namespace) (kube_persistentvolumeclaim_resource_requests_storage_bytes)
```
##Row 5: Critical Platform Controllers
###Panel: EBS CSI Controller Available

####Type: Stat

```text
kube_deployment_status_replicas_available{
  namespace="kube-system",
  deployment="ebs-csi-controller"
}
```
###Panel: AWS Load Balancer Controller Available

####Type: Stat

```text
kube_deployment_status_replicas_available{
  namespace="kube-system",
  deployment="aws-load-balancer-controller"
}
```
###Panel: CoreDNS Available

####Type: Stat

```text
kube_deployment_status_replicas_available{
  namespace="kube-system",
  deployment="coredns"
}
```
##Row 6: Monitoring Stack Health
###Panel: Prometheus Ready

####Type: Stat

```text
up{job=~".*prometheus.*"}
```
###Panel: Grafana Available

####Type: Stat

```text
kube_deployment_status_replicas_available{
  namespace="monitoring",
  deployment="kps-grafana"
}
```
###Panel: Alertmanager Ready

####Type: Stat

```text
up{job=~".*alertmanager.*"}
```

##Initial Platform SLO Candidates


| SLO                              | SLI                                          | Target                       |
| -------------------------------- | -------------------------------------------- | ---------------------------- |
| Node readiness                   | Ready nodes / total nodes                    | 100% during normal operation |
| Critical controller availability | Available replicas for platform controllers  | 99.9%                        |
| PVC provisioning health          | Pending PVC count                            | 0 pending PVCs > 5 minutes   |
| Pod stability                    | CrashLoopBackOff pods                        | 0 critical pods              |
| Monitoring availability          | Prometheus/Grafana/Alertmanager availability | 99.9%                        |

## Implementation Status

Status: Implemented in Grafana and exported as JSON.

Dashboard JSON:

```text
dashboards/platform/platform-observability-baseline.json
dashboards/platform/platform-observability-baseline2.json
dashboards/platform/platform-observability-baseline3.json
```
Current rows:

- Cluster Overview
- Node Resource Saturation
- Pod Health
- Storage Health
- Critical Platform Controllers
- Monitoring Stack Health