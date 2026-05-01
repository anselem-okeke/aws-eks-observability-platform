# Alertmanager Routing Design

## Purpose

This document describes the initial Alertmanager routing model for the AWS SRE Observability Platform.

The goal is to group alerts by severity, platform area, and workload ownership.

## Routing Flow

```text
PrometheusRule
  -> Prometheus
  -> Alertmanager
  -> route by severity / area / app
```
##Labels Used for Routing

| Label      | Purpose               | Example                                                  |
| ---------- | --------------------- | -------------------------------------------------------- |
| `severity` | Alert urgency         | `critical`, `warning`                                    |
| `area`     | Platform area         | `platform`, `storage`, `ingress`, `database`, `workload` |
| `app`      | Application ownership | `bank-of-anthos`                                         |

##Receivers
| Receiver          | Purpose                                       |
| ----------------- | --------------------------------------------- |
| `critical-alerts` | Critical alerts requiring immediate attention |
| `warning-alerts`  | Warning alerts requiring investigation        |
| `platform-alerts` | Kubernetes/platform health alerts             |
| `workload-alerts` | Application workload health alerts            |
| `ingress-alerts`  | ALB / ingress related alerts                  |
| `storage-alerts`  | EBS CSI / PVC related alerts                  |
| `database-alerts` | Stateful database related alerts              |

##Current Notification Mode

The current configuration is local-only.

Alerts are routed inside Alertmanager but are not yet sent to Slack, email, PagerDuty, or webhook receivers.

##Future Integrations

Possible next integrations:

- Slack webhook
- Email receiver
- PagerDuty
- OpsGenie
- Webhook receiver
- Incident runbook links