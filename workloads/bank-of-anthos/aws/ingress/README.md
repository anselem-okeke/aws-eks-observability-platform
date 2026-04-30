# Cloudflare DNS + AWS ACM + EKS ALB HTTPS Setup

## Goal

Expose the Bank of Anthos frontend through a clean HTTPS domain instead of using the raw AWS ALB DNS name.

Final access path:

```text
Browser
  → Cloudflare DNS
  → AWS Application Load Balancer
  → EKS Ingress
  → Kubernetes Service
  → Frontend Pod
```
Final URL example:

```text
https://bank.anselemokeke.dpdns.org
```
##1. Current working ALB endpoint

The EKS Ingress created an AWS ALB:

```text
k8s-fintechw-bankofan-7a71342d9f-255438134.eu-central-1.elb.amazonaws.com
```

HTTP access was confirmed:

```text
curl -I http://k8s-fintechw-bankofan-7a71342d9f-255438134.eu-central-1.elb.amazonaws.com

```
Expected:

```text
HTTP/1.1 200 OK
```
##2. Create ACM certificate in the ALB region

Because the ALB runs in eu-central-1, the ACM certificate must also be in eu-central-1.

```shell
aws acm request-certificate \
  --region eu-central-1 \
  --domain-name "*.anselemokeke.dpdns.org" \
  --validation-method DNS \
  --query "CertificateArn" \
  --output text
```

Save the ARN:


```shell
export CERT_ARN_EU="arn:aws:acm:eu-central-1:521544431137:certificate/0218e3f6-a35f-4839-bf7a-1138deffc500"
```
##3. Get the ACM DNS validation record
```shell
aws acm describe-certificate \
  --region eu-central-1 \
  --certificate-arn "$CERT_ARN_EU" \
  --query "Certificate.DomainValidationOptions[*].ResourceRecord" \
  --output table
```
Example output:

```shell
Name:
_662191d447d5c18f7cf3f370a7efc7f3.anselemokeke.dpdns.org

Type:
CNAME

Value:
_d66a611d341d9a1789bbd6bd43e308d2.jkddzztzsm.acm-validations.aws
```
##4. Add ACM validation CNAME in Cloudflare

- Go to:
  - `Cloudflare → DNS → Records → Add record`

- Add:


| Field        | Value                                                              |
| ------------ | ------------------------------------------------------------------ |
| Type         | CNAME                                                              |
| Name         | `_662191d447d5c18f7cf3f370a7efc7f3`                                |
| Target       | `_d66a611d341d9a1789bbd6bd43e308d2.jkddzztzsm.acm-validations.aws` |
| Proxy status | DNS only                                                           |
| TTL          | Auto                                                               |

Important:

```shell
ACM validation records must be DNS only.
Do not enable Cloudflare proxy for this record.
```

Check certificate status:

```shell
aws acm describe-certificate \
  --region eu-central-1 \
  --certificate-arn "$CERT_ARN_EU" \
  --query "Certificate.Status" \
  --output text
```

Expected:

- ISSUED
##5. Attach certificate to the EKS Ingress
- This patch below changes it from traditional HTTP to HTTPS
```shell
kubectl -n fintech-workload annotate ingress bank-of-anthos-frontend \
  alb.ingress.kubernetes.io/listen-ports='[{"HTTP":80},{"HTTPS":443}]' \
  alb.ingress.kubernetes.io/certificate-arn="$CERT_ARN_EU" \
  alb.ingress.kubernetes.io/ssl-redirect='443' \
  --overwrite
```
##6. Verify ALB listeners
```shell
ALB_DNS=$(kubectl -n fintech-workload get ingress bank-of-anthos-frontend \
  -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

ALB_ARN=$(aws elbv2 describe-load-balancers \
  --region eu-central-1 \
  --query "LoadBalancers[?DNSName=='$ALB_DNS'].LoadBalancerArn" \
  --output text)

aws elbv2 describe-listeners \
  --region eu-central-1 \
  --load-balancer-arn "$ALB_ARN" \
  --query "Listeners[*].[Port,Protocol,Certificates[0].CertificateArn,DefaultActions[0].Type]" \
  --output table
```

Expected:

```shell
443  HTTPS  arn:aws:acm:eu-central-1:...  fixed-response
80   HTTP   None                           redirect
```
##7. Add application DNS record in Cloudflare

This is where the application name is chosen.

- Go to:

  - Cloudflare → DNS → Records → Add record

- Add:

| Field        | Value                                                                       |
| ------------ | --------------------------------------------------------------------------- |
| Type         | CNAME                                                                       |
| Name         | `bank`                                                                      |
| Target       | `k8s-fintechw-bankofan-7a71342d9f-255438134.eu-central-1.elb.amazonaws.com` |
| Proxy status | DNS only first                                                              |
| TTL          | Auto                                                                        |


This creates:

```shell
bank.anselemokeke.dpdns.org
```
##8. Test HTTPS access
```shell
curl -I https://bank.anselemokeke.dpdns.org
```

Expected:

```text
HTTP/2 200

or:

HTTP/1.1 200 OK
```

Also test HTTP redirect:

```text
curl -I http://bank.anselemokeke.dpdns.org
```

Expected:

```text
301 or 302 redirect to HTTPS
```
##Important Concepts
```text
ACM validation CNAME

Used only to prove domain ownership to AWS.

_662191d... → _d66a...acm-validations.aws
Application CNAME

Used by users/browsers to reach the application.

bank → AWS ALB DNS
Why the old us-east-1 certificate was not used
```

> The existing certificate in us-east-1 can be useful for CloudFront, but an ALB in eu-central-1 requires an ACM certificate in eu-central-1.

##Final Architecture
```text
User / Browser
  → HTTPS
Cloudflare DNS
  → bank.anselemokeke.dpdns.org
AWS ALB :443
  → EKS Ingress
Kubernetes Service :8080
  → Bank of Anthos Frontend Pod
```