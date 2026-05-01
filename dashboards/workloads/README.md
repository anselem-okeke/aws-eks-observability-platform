## Bank of Anthos Workload Observability Baseline

## Purpose

This dashboard provides the first workload-level visibility layer for the Bank of Anthos application running on EKS.

It focuses on Kubernetes workload health before deeper application metrics, logs, traces, and SLOs are added.

## Namespace

```text
fintech-workload
```
##Dashboard Scope

This dashboard covers:

- Workload pod health
- Deployment availability
- Pod restarts
- CPU usage
- Memory usage
- Service inventory
- Ingress visibility
- Persistent database pod health

##Row 1: Workload Overview
###Panel: Running Pods

####Type: Stat

```text
sum(kube_pod_status_phase{namespace="fintech-workload",phase="Running"})
```
###Panel: Pods Not Running

####Type: Stat

```text
sum(kube_pod_status_phase{namespace="fintech-workload",phase=~"Pending|Failed|Unknown"})
```
###Panel: Deployments Available

####Type: Stat

```text
sum(kube_deployment_status_replicas_available{namespace="fintech-workload"})
```
###Panel: Services Count

####Type: Stat

```text
count(kube_service_info{namespace="fintech-workload"})
```
##Row 2: Pod Health
###Panel: Pod Restarts - 15m

####Type: Bar gauge / Table

```text
sum by (pod) (
  increase(kube_pod_container_status_restarts_total{namespace="fintech-workload"}[15m])
)
```
###Panel: CrashLoopBackOff Pods

####Type: Table

```text
kube_pod_container_status_waiting_reason{
  namespace="fintech-workload",
  reason="CrashLoopBackOff"
}
```
###Panel: Pending Pods

####Type: Table

```text
kube_pod_status_phase{
  namespace="fintech-workload",
  phase="Pending"
} == 1
```
##Row 3: Resource Usage
###Panel: CPU Usage by Pod

####Type: Time series

```text
sum by (pod) (
  rate(container_cpu_usage_seconds_total{
    namespace="fintech-workload",
    container!="",
    pod!=""
  }[5m])
)
```
###Panel: Memory Usage by Pod

####Type: Time series

```text
sum by (pod) (
  container_memory_working_set_bytes{
    namespace="fintech-workload",
    container!="",
    pod!=""
  }
)
```
###Panel: CPU Usage by Workload

####Type: Bar gauge

```text
sum by (pod) (
  rate(container_cpu_usage_seconds_total{
    namespace="fintech-workload",
    container!="",
    pod!=""
  }[5m])
)
```
###Panel: Memory Usage by Workload

####Type: Bar gauge

```text
sum by (pod) (
  container_memory_working_set_bytes{
    namespace="fintech-workload",
    container!="",
    pod!=""
  }
)
```
##Row 4: Deployment Health
###Panel: Available Replicas by Deployment

####Type: Bar gauge

```text
kube_deployment_status_replicas_available{
  namespace="fintech-workload"
}
```
###Panel: Desired Replicas by Deployment

####Type: Bar gauge

```text
kube_deployment_spec_replicas{
  namespace="fintech-workload"
}
```
###Panel: Unavailable Replicas by Deployment

####Type: Table / Stat

```text
kube_deployment_status_replicas_unavailable{
  namespace="fintech-workload"
}
```
##Row 5: Stateful Database Health
###Panel: StatefulSets Ready

####Type: Stat

```text
sum(kube_statefulset_status_replicas_ready{namespace="fintech-workload"})
```
###Panel: StatefulSet Ready Replicas

####Type: Bar gauge

```text
kube_statefulset_status_replicas_ready{
  namespace="fintech-workload"
}
```
###Panel: StatefulSet Desired Replicas

####Type: Bar gauge

```text
kube_statefulset_replicas{
  namespace="fintech-workload"
}
```
##Row 6: Ingress Health
###Panel: Ingress Count

####Type: Stat

```text
count(kube_ingress_info{namespace="fintech-workload"})
```
###Panel: Ingress Info

####Type: Table

```text
kube_ingress_info{namespace="fintech-workload"}
```

##Initial Workload SLO Candidates

| SLO                       | SLI                                      | Target                        |
| ------------------------- | ---------------------------------------- | ----------------------------- |
| Workload pod availability | Running pods / expected pods             | 99.5%                         |
| Frontend availability     | Frontend pod ready and service reachable | 99.5%                         |
| Pod stability             | Restart count                            | No unexpected restarts in 15m |
| Database availability     | DB StatefulSet ready replicas            | 99%                           |
| Ingress availability      | ALB ingress present and routable         | 99.5%                         |
