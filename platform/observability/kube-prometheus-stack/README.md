# Kube Prometheus Stack

This directory contains the Helm values for installing the platform observability foundation.

## Purpose

The kube-prometheus-stack provides the metrics foundation for the AWS SRE Observability Platform.

It installs:

- Prometheus
- Grafana
- Alertmanager
- kube-state-metrics
- node-exporter
- Prometheus Operator

## Namespace

```text
monitoring
```
## Install
```shell
kubectl create namespace monitoring

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update prometheus-community

helm upgrade --install kps prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  -f platform/observability/kube-prometheus-stack/values.yaml
```
##Validate
```shell
kubectl -n monitoring get pods
kubectl -n monitoring get pvc
kubectl -n monitoring get svc
```
##Access Grafana
```shell
kubectl -n monitoring port-forward svc/kps-grafana 3000:80
```
```text

Open:

http://localhost:3000

Default lab credentials:

admin / admin123
Access Prometheus
kubectl -n monitoring port-forward svc/kps-prometheus 9090:9090

Open:

http://localhost:9090/targets
Storage

Prometheus, Grafana, and Alertmanager use the gp3 StorageClass backed by AWS EBS CSI.

```

---

##Commit

After validation:

```bash
git status
git add platform/observability/kube-prometheus-stack/
git commit -m "Add platform observability foundation with kube-prometheus-stack"
```