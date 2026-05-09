# AWS Billing & Cost Safety Runbook

## Purpose

This runbook helps verify whether AWS resources are still consuming credits after cleanup.

Use it before and after major project phases such as:

- EKS cluster creation
- OpenSearch deployment
- LoadBalancer testing
- NAT Gateway usage
- EBS/PVC creation
- Full Terraform destroy

---

## 1. Check Remaining Free Tier Credits


```shell
aws freetier get-account-plan-state \
  --region us-east-1 \
  --query "accountPlanRemainingCredits" \
  --output table
```
```text

Expected output:

+----------+--------+
| amount   | unit   |
+----------+--------+
| 128.94   | USD    |
+----------+--------+
```

Record the value before and after every major phase.

##2. Check Cost by AWS Service
```shell
START=$(date -u -d "3 days ago" +%Y-%m-%d)
END=$(date -u -d "tomorrow" +%Y-%m-%d)

aws ce get-cost-and-usage \
  --time-period Start=$START,End=$END \
  --granularity DAILY \
  --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --region us-east-1 \
  --output table
```
- Look for these services:

| Service                                | Possible Meaning                    |
| -------------------------------------- | ----------------------------------- |
| Amazon Elastic Kubernetes Service      | EKS control plane still active      |
| Amazon Elastic Compute Cloud - Compute | EC2 nodes or jumpbox still running  |
| EC2 - Other                            | EBS volumes, snapshots, Elastic IPs |
| Amazon OpenSearch Service              | OpenSearch domain still running     |
| Amazon Elastic Load Balancing          | ALB/NLB still active                |
| Amazon Virtual Private Cloud           | NAT Gateway, VPC endpoints          |
| AmazonCloudWatch                       | Logs, metrics, alarms               |

##3. Check Cost by Usage Type

Use this to identify what EC2 - Other or hidden cost actually means.

```shell
START=$(date -u -d "3 days ago" +%Y-%m-%d)
END=$(date -u -d "tomorrow" +%Y-%m-%d)

aws ce get-cost-and-usage \
  --time-period Start=$START,End=$END \
  --granularity DAILY \
  --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=USAGE_TYPE \
  --region us-east-1 \
  --query "ResultsByTime[].Groups[?Metrics.UnblendedCost.Amount!='0'][].[Keys[0],Metrics.UnblendedCost.Amount,Metrics.UnblendedCost.Unit]" \
  --output table
```
- Common usage types:

| Usage Type            | Meaning                     |
| --------------------- | --------------------------- |
| `EKS-Hours`           | EKS control plane cost      |
| `BoxUsage`            | EC2 instance runtime        |
| `EBS:VolumeUsage.gp3` | gp3 EBS volume storage      |
| `EBS:SnapshotUsage`   | EBS snapshot storage        |
| `NatGateway-Hours`    | NAT Gateway hourly charge   |
| `NatGateway-Bytes`    | NAT Gateway data processing |
| `LCUUsage`            | Load Balancer usage         |
| `DataTransfer`        | Network transfer cost       |


##4. Check Active EKS Clusters
```shell
aws eks list-clusters \
  --region eu-central-1 \
  --output table
```

If a cluster is still listed, check status:

```shell
aws eks describe-cluster \
  --name <cluster-name> \
  --region eu-central-1 \
  --query "cluster.{Name:name,Status:status,CreatedAt:createdAt}" \
  --output table
```

If status is ACTIVE, the cluster may still consume cost.

##5. Check EC2 Instances
```shell
aws ec2 describe-instances \
  --region eu-central-1 \
  --query "Reservations[].Instances[].[InstanceId,State.Name,InstanceType,PublicIpAddress,Tags[?Key=='Name'].Value|[0]]" \
  --output table
```

Look for:

- running

Stop unused instances:

```shell
aws ec2 stop-instances \
  --region eu-central-1 \
  --instance-ids <instance-id>
```

Terminate only when no longer needed:

```shell
aws ec2 terminate-instances \
  --region eu-central-1 \
  --instance-ids <instance-id>
```
##6. Check EBS Volumes
```shell
aws ec2 describe-volumes \
  --region eu-central-1 \
  --query "Volumes[].[VolumeId,State,Size,VolumeType,Attachments[0].InstanceId,Tags[?Key=='Name'].Value|[0]]" \
  --output table
```

Volumes in this state still cost money:

- available

Delete unused detached volumes:

```shell
aws ec2 delete-volume \
  --region eu-central-1 \
  --volume-id <volume-id>
```
##7. Check EBS Snapshots
```shell
aws ec2 describe-snapshots \
  --region eu-central-1 \
  --owner-ids self \
  --query "Snapshots[].[SnapshotId,VolumeSize,StartTime,Description]" \
  --output table
```

Delete unused snapshots:

```shell
aws ec2 delete-snapshot \
  --region eu-central-1 \
  --snapshot-id <snapshot-id>
```
##8. Check Load Balancers
```shell
aws elbv2 describe-load-balancers \
  --region eu-central-1 \
  --query "LoadBalancers[].[LoadBalancerName,Type,State.Code,VpcId]" \
  --output table
```

Get ARNs if deletion is needed:

```shell
aws elbv2 describe-load-balancers \
  --region eu-central-1 \
  --query "LoadBalancers[].[LoadBalancerName,LoadBalancerArn]" \
  --output table
```

Delete unused load balancer:

```shell
aws elbv2 delete-load-balancer \
  --region eu-central-1 \
  --load-balancer-arn <load-balancer-arn>
```
##9. Check NAT Gateways
```shell
aws ec2 describe-nat-gateways \
  --region eu-central-1 \
  --query "NatGateways[].[NatGatewayId,State,VpcId,SubnetId,Tags[?Key=='Name'].Value|[0]]" \
  --output table
```

If state is:

- available

it is still charging.

Delete unused NAT Gateway:

```shell
aws ec2 delete-nat-gateway \
  --region eu-central-1 \
  --nat-gateway-id <nat-gateway-id>
```
##10. Check Elastic IPs
```shell
aws ec2 describe-addresses \
  --region eu-central-1 \
  --query "Addresses[].[AllocationId,PublicIp,AssociationId,InstanceId,NetworkInterfaceId]" \
  --output table
```

If AssociationId is empty, release it:

```shell
aws ec2 release-address \
  --region eu-central-1 \
  --allocation-id <allocation-id>
```
##11. Check OpenSearch Domains
```shell
aws opensearch list-domain-names \
  --region eu-central-1 \
  --output table
```

Describe domain:

```shell
aws opensearch describe-domain \
  --region eu-central-1 \
  --domain-name <domain-name> \
  --query "DomainStatus.{Name:DomainName,Processing:Processing,Endpoint:Endpoint,EngineVersion:EngineVersion}" \
  --output table
```

Delete unused domain:

```shell
aws opensearch delete-domain \
  --region eu-central-1 \
  --domain-name <domain-name>
```
##12. Check CloudWatch Log Groups
```shell
aws logs describe-log-groups \
  --region eu-central-1 \
  --query "logGroups[].[logGroupName,storedBytes,retentionInDays]" \
  --output table
```

Set 7-day retention:

```shell
aws logs put-retention-policy \
  --region eu-central-1 \
  --log-group-name "<log-group-name>" \
  --retention-in-days 7
```

Delete unused log group:

```shell
aws logs delete-log-group \
  --region eu-central-1 \
  --log-group-name "<log-group-name>"
```
##13. Quick Full Safety Check

Run this after cleanup:

```shell
aws eks list-clusters --region eu-central-1 --output table

aws ec2 describe-instances \
  --region eu-central-1 \
  --query "Reservations[].Instances[].[InstanceId,State.Name,InstanceType,Tags[?Key=='Name'].Value|[0]]" \
  --output table

aws ec2 describe-volumes \
  --region eu-central-1 \
  --query "Volumes[].[VolumeId,State,Size,VolumeType,Attachments[0].InstanceId]" \
  --output table

aws ec2 describe-snapshots \
  --region eu-central-1 \
  --owner-ids self \
  --query "Snapshots[].[SnapshotId,VolumeSize,StartTime,Description]" \
  --output table

aws elbv2 describe-load-balancers \
  --region eu-central-1 \
  --query "LoadBalancers[].[LoadBalancerName,Type,State.Code,VpcId]" \
  --output table

aws ec2 describe-nat-gateways \
  --region eu-central-1 \
  --query "NatGateways[].[NatGatewayId,State,VpcId,SubnetId]" \
  --output table

aws ec2 describe-addresses \
  --region eu-central-1 \
  --query "Addresses[].[AllocationId,PublicIp,AssociationId,InstanceId]" \
  --output table

aws opensearch list-domain-names \
  --region eu-central-1 \
  --output table
```
##14. Interpretation Pattern

Use this structure when investigating cost:

```shell
Problem:
AWS credits are decreasing after cleanup.

Signal:
Free-tier credit balance dropped.

Investigation:
Check Cost Explorer by SERVICE and USAGE_TYPE.

Action:
Find and delete active resources: EKS, EC2, EBS, NAT, Load Balancer, OpenSearch.

Improvement:
Check credits before and after each project phase.
Use short-lived infrastructure.
Destroy expensive resources after evidence capture.
```
##15. Safe Operating Rule for This Project

Before starting a phase:

```shell
aws freetier get-account-plan-state \
  --region us-east-1 \
  --query "accountPlanRemainingCredits" \
  --output table
```

After finishing a phase:

```shell
aws ce get-cost-and-usage \
  --time-period Start=$(date -u -d "1 day ago" +%Y-%m-%d),End=$(date -u -d "tomorrow" +%Y-%m-%d) \
  --granularity DAILY \
  --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --region us-east-1 \
  --output table
```

Recommended project workflow:

```text
Create resources → deploy phase → capture screenshots/evidence → destroy expensive resources → verify billing
```
##16. High-Risk Cost Services

Treat these as expensive:

| Priority | Service                   |
| -------: | ------------------------- |
|        1 | OpenSearch                |
|        2 | NAT Gateway               |
|        3 | EKS control plane         |
|        4 | EC2 worker nodes          |
|        5 | Load Balancers            |
|        6 | EBS volumes and snapshots |
|        7 | CloudWatch logs           |
