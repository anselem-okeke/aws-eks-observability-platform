# OpenSearch Logging Backend

OpenSearch is used as the log storage and search backend for the AWS SRE Observability Platform.

## Purpose

Stores Kubernetes container logs collected by Fluent Bit.

## Namespace

```text
logging
```
##Install
```shell
helm repo add opensearch https://opensearch-project.github.io/helm-charts/
helm repo update opensearch

helm upgrade --install opensearch opensearch/opensearch \
  --namespace logging \
  -f platform/logging/opensearch/values.yaml
```
##Validate
```shell
kubectl -n logging get pods
kubectl -n logging get pvc
kubectl -n logging port-forward svc/opensearch-main 9200:9200
curl http://localhost:9200
curl "http://localhost:9200/_cat/indices?v"
```

##Fluent Bit Log Collector

Fluent Bit collects Kubernetes container logs and ships them to OpenSearch.

## Flow

```text
/var/log/containers/*.log
  -> Fluent Bit DaemonSet
  -> OpenSearch
  -> kubernetes-logs index
```
##Namespace
```shell
logging
```
##Install
```shell
helm repo add fluent https://fluent.github.io/helm-charts
helm repo update fluent

helm upgrade --install fluent-bit fluent/fluent-bit \
  --namespace logging \
  -f platform/logging/fluent-bit/values.yaml
```
##Validate
```shell
kubectl -n logging get pods -l app.kubernetes.io/name=fluent-bit
kubectl -n logging logs -l app.kubernetes.io/name=fluent-bit --tail=80
curl "http://localhost:9200/_cat/indices?v"
```