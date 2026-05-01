# OpenSearch Operational Log Queries

## Purpose

This runbook contains useful OpenSearch queries for investigating platform and workload issues in the AWS SRE Observability Platform.

Logs are collected by Fluent Bit and stored in OpenSearch.

## Log Flow

```text
Kubernetes container logs
  -> Fluent Bit DaemonSet
  -> OpenSearch
  -> kubernetes-logs index
```
##Index
```shell
kubernetes-logs
```
##Access OpenSearch

```shell
Port-forward OpenSearch:

kubectl -n logging port-forward svc/opensearch-main 9200:9200

Test connection:

curl http://localhost:9200

List indices:

curl "http://localhost:9200/_cat/indices?v"
```
##1. Inspect Sample Logs

Use this query to inspect the document structure.

```shell
curl -s "http://localhost:9200/kubernetes-logs/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 3,
    "query": {
      "match_all": {}
    }
  }'
```

Use this first whenever field names are unclear.

##2. Search Logs by Namespace
Bank of Anthos workload logs
```shell
curl -s "http://localhost:9200/kubernetes-logs/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 10,
    "query": {
      "term": {
        "kubernetes.namespace_name.keyword": "fintech-workload"
      }
    }
  }'
```
Platform logs from kube-system
```shell
curl -s "http://localhost:9200/kubernetes-logs/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 10,
    "query": {
      "term": {
        "kubernetes.namespace_name.keyword": "kube-system"
      }
    }
  }'
```
Monitoring stack logs
```shell
curl -s "http://localhost:9200/kubernetes-logs/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 10,
    "query": {
      "term": {
        "kubernetes.namespace_name.keyword": "monitoring"
      }
    }
  }'
```
##3. Search Logs by Pod Name

Replace the pod name with the pod you want to investigate.

```shell
curl -s "http://localhost:9200/kubernetes-logs/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 20,
    "query": {
      "term": {
        "kubernetes.pod_name.keyword": "frontend-REPLACE-ME"
      }
    }
  }'
```

To get current pod names:

```shell
kubectl -n fintech-workload get pods
```
##4. Search Logs by Container Name
Frontend logs
```shell
curl -s "http://localhost:9200/kubernetes-logs/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 20,
    "query": {
      "term": {
        "kubernetes.container_name.keyword": "frontend"
      }
    }
  }'
```
Userservice logs
```shell
curl -s "http://localhost:9200/kubernetes-logs/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 20,
    "query": {
      "term": {
        "kubernetes.container_name.keyword": "userservice"
      }
    }
  }'
```
##5. Search for Errors
Generic error search
```shell
curl -s "http://localhost:9200/kubernetes-logs/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 20,
    "query": {
      "query_string": {
        "query": "error OR exception OR failed OR timeout"
      }
    }
  }'
```
Errors only in Bank of Anthos namespace
```shell
curl -s "http://localhost:9200/kubernetes-logs/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 20,
    "query": {
      "bool": {
        "must": [
          {
            "term": {
              "kubernetes.namespace_name.keyword": "fintech-workload"
            }
          },
          {
            "query_string": {
              "query": "error OR exception OR failed OR timeout"
            }
          }
        ]
      }
    }
  }'
```
##6. Search Recent Logs

Use this if timestamp parsing is available in the indexed documents.

```shell
curl -s "http://localhost:9200/kubernetes-logs/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 20,
    "sort": [
      {
        "@timestamp": {
          "order": "desc"
        }
      }
    ],
    "query": {
      "range": {
        "@timestamp": {
          "gte": "now-15m"
        }
      }
    }
  }'
```
##7. AWS Load Balancer Controller Logs

Useful when Ingress does not create an ALB or target groups fail.

```shell
curl -s "http://localhost:9200/kubernetes-logs/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 20,
    "query": {
      "term": {
        "kubernetes.container_name.keyword": "aws-load-balancer-controller"
      }
    }
  }'
```

Search ALB controller errors:

```shell
curl -s "http://localhost:9200/kubernetes-logs/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 20,
    "query": {
      "bool": {
        "must": [
          {
            "term": {
              "kubernetes.container_name.keyword": "aws-load-balancer-controller"
            }
          },
          {
            "query_string": {
              "query": "error OR AccessDenied OR failed OR reconcile"
            }
          }
        ]
      }
    }
  }'
```
##8. EBS CSI Driver Logs

Useful when PVCs are stuck Pending or volumes fail to attach.

```shell
curl -s "http://localhost:9200/kubernetes-logs/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 20,
    "query": {
      "query_string": {
        "query": "ebs-csi-controller OR ebs-plugin OR csi.sock OR CreateVolume OR AttachVolume"
      }
    }
  }'
```

Search EBS CSI errors:

```shell
curl -s "http://localhost:9200/kubernetes-logs/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 20,
    "query": {
      "query_string": {
        "query": "EBS OR ebs-plugin OR CreateVolume OR AttachVolume AND error OR failed OR AccessDenied"
      }
    }
  }'
```
##9. Fluent Bit Pipeline Health

Search Fluent Bit logs:

```shell
curl -s "http://localhost:9200/kubernetes-logs/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 20,
    "query": {
      "term": {
        "kubernetes.container_name.keyword": "fluent-bit"
      }
    }
  }'
```

Search Fluent Bit errors:

```shell
curl -s "http://localhost:9200/kubernetes-logs/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 20,
    "query": {
      "bool": {
        "must": [
          {
            "term": {
              "kubernetes.container_name.keyword": "fluent-bit"
            }
          },
          {
            "query_string": {
              "query": "error OR failed OR retry OR connection"
            }
          }
        ]
      }
    }
  }'
```
##10. Useful Kubernetes Commands During Log Investigation
Get workload pods
```shell
kubectl -n fintech-workload get pods -o wide
```
Get recent Kubernetes events
```shell
kubectl -n fintech-workload get events --sort-by=.lastTimestamp | tail -50
```
Compare OpenSearch logs with kubectl logs
```shell
kubectl -n fintech-workload logs deploy/frontend --tail=100
```
Check Fluent Bit status
```shell
kubectl -n logging get pods -l app.kubernetes.io/name=fluent-bit
kubectl -n logging logs -l app.kubernetes.io/name=fluent-bit --tail=100
```
##Investigation Workflow

Order during incidents:

```text
1. Check Grafana dashboard
2. Identify affected namespace / pod / service
3. Check Prometheus alert
4. Query OpenSearch logs for the same namespace or pod
5. Check Kubernetes events
6. Compare with kubectl logs if needed
7. Document finding in runbook
```