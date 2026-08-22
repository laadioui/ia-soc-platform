# Deployment Overview — AI SOC Platform

## Environments

| Environment | Purpose | Infrastructure |
|-------------|---------|----------------|
| **local** | Development | Docker Compose |
| **staging** | Pre-production testing | EKS (minimal) |
| **production** | Production SOC | EKS (HA) + AWS managed services |

---

## Local Development (Docker Compose)

```mermaid
flowchart TB
    subgraph DockerCompose["Docker Compose — Local Dev"]
        PG[PostgreSQL 16<br/>:5432]
        REDIS[Redis 7<br/>:6379]
        KAFKA[Kafka KRaft<br/>:9092]
        KUI[Kafka UI<br/>:8085]
        OS[OpenSearch 2.x<br/>:9200]
        OSD[OpenSearch Dashboards<br/>:5601]
        KC[Keycloak 24<br/>:8080]
        PROM[Prometheus<br/>:9090]
        GRAF[Grafana<br/>:3001]
    end

    subgraph AppServices["Application (Phase 3+)"]
        GW[api-gateway :8000]
        SVC[Microservices :8001-8008]
        FE[frontend :3000]
    end

    AppServices --> DockerCompose
```

**Commandes** :
```bash
cp .env.example .env
make up          # Start infrastructure
make up-all      # Start infra + app services (Phase 3+)
make down        # Stop everything
make logs        # Tail logs
make ps          # Service status
```

---

## Kubernetes (Production)

```mermaid
flowchart TB
    subgraph EKS["Amazon EKS"]
        subgraph NS_Frontend["namespace: ai-soc-frontend"]
            FE[frontend<br/>Deployment replicas:2]
        end

        subgraph NS_Gateway["namespace: ai-soc-gateway"]
            GW[api-gateway<br/>Deployment replicas:3 HPA]
        end

        subgraph NS_Services["namespace: ai-soc-services"]
            AUTH[auth-service]
            COLL[collector-service<br/>replicas:3 HPA]
            DET[detection-service<br/>replicas:3 HPA]
            CORR[correlation-service]
            TI[threat-intelligence-service]
            INC[incident-service]
            AI[ai-service]
            NOTIF[notification-service]
        end

        subgraph NS_Infra["namespace: ai-soc-infra"]
            KAFKA[Strimzi Kafka]
            OS[OpenSearch Operator]
            KC[Keycloak]
            PROM[Prometheus Operator]
            GRAF[Grafana]
        end

        INGRESS[Ingress / ALB]
    end

    subgraph AWS_Managed["AWS Managed"]
        RDS[(RDS PostgreSQL<br/>Multi-AZ)]
        EC[(ElastiCache Redis)]
        S3[(S3 Backups/Models)]
        SM[Secrets Manager]
    end

    INGRESS --> NS_Frontend & NS_Gateway
    NS_Services --> RDS & EC & KAFKA & OS & SM
```

**Deploy** :
```bash
# Via Helm
helm install ai-soc ./infrastructure/helm/ai-soc-platform \
  --namespace ai-soc \
  --values infrastructure/helm/values-production.yaml

# Via ArgoCD (GitOps)
kubectl apply -f infrastructure/kubernetes/argocd/application.yaml
```

---

## AWS Architecture (Terraform)

```mermaid
flowchart TB
    subgraph AWS
        subgraph VPC
            subgraph PublicSubnets
                ALB[Application Load Balancer]
                NAT[NAT Gateway]
            end

            subgraph PrivateSubnets
                EKS[EKS Cluster]
                RDS[(RDS PostgreSQL<br/>Multi-AZ)]
                EC[(ElastiCache Redis<br/>Cluster Mode)]
            end
        end

        S3[(S3<br/>Backups, ML Models, Logs)]
        SM[Secrets Manager]
        CW[CloudWatch]
        IAM[IAM Roles<br/>IRSA]
        R53[Route 53<br/>DNS]
        ACM[ACM<br/>TLS Certificates]
    end

    Internet --> ALB
    ALB --> EKS
    EKS --> RDS & EC & S3 & SM
    EKS --> CW
    IAM --> EKS
    R53 --> ALB
    ACM --> ALB
```

**Terraform** :
```bash
cd infrastructure/terraform/environments/staging
terraform init
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

---

## Port Mapping (Local Dev)

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| API Gateway | 8000 | http://localhost:8000 |
| Auth Service | 8001 | http://localhost:8001 |
| Collector Service | 8002 | http://localhost:8002 |
| Detection Service | 8003 | http://localhost:8003 |
| Correlation Service | 8004 | http://localhost:8004 |
| Threat Intel Service | 8005 | http://localhost:8005 |
| Incident Service | 8006 | http://localhost:8006 |
| AI Service | 8007 | http://localhost:8007 |
| Notification Service | 8008 | http://localhost:8008 |
| Keycloak | 8080 | http://localhost:8080 |
| Kafka UI | 8085 | http://localhost:8085 |
| PostgreSQL | 5432 | localhost:5432 |
| Redis | 6379 | localhost:6379 |
| Kafka | 9092 | localhost:9092 |
| OpenSearch | 9200 | http://localhost:9200 |
| OpenSearch Dashboards | 5601 | http://localhost:5601 |
| Prometheus | 9090 | http://localhost:9090 |
| Grafana | 3001 | http://localhost:3001 |

---

## Resource Requirements

### Local Development (minimum)

| Resource | Minimum |
|----------|---------|
| CPU | 4 cores |
| RAM | 16 GB |
| Disk | 30 GB |

### Production (EKS)

| Component | Spec |
|-----------|------|
| EKS Nodes | 3x m5.xlarge (4 vCPU, 16 GB) |
| RDS PostgreSQL | db.r6g.large, Multi-AZ |
| ElastiCache Redis | cache.r6g.large, 2 nodes |
| OpenSearch | 3x r6g.large.search |
| Kafka (Strimzi) | 3 brokers, 3x m5.large |

---

## CI/CD Pipeline

```mermaid
flowchart LR
    PUSH[git push] --> LINT[Lint<br/>ruff + eslint]
    LINT --> TEST[Unit Tests<br/>pytest + jest]
    TEST --> SAST[SAST<br/>Semgrep]
    SAST --> DEPS[Dependency Scan<br/>pip-audit + npm audit]
    DEPS --> SECRETS[Secret Scan<br/>Gitleaks]
    SECRETS --> BUILD[Build Docker Images]
    BUILD --> TRIVY[Container Scan<br/>Trivy]
    TRIVY --> INT[Integration Tests]
    INT --> DAST[DAST<br/>OWASP ZAP]
    DAST --> PUSH_REG[Push to Registry]
    PUSH_REG --> DEPLOY[Deploy<br/>ArgoCD]
```

---

## Secrets Management

| Secret | Local (.env) | Production |
|--------|-------------|------------|
| PostgreSQL password | `.env` | AWS Secrets Manager |
| Redis password | `.env` | AWS Secrets Manager |
| Keycloak admin | `.env` | AWS Secrets Manager |
| JWT secret | `.env` | AWS Secrets Manager |
| LLM API key | `.env` | AWS Secrets Manager |
| Kafka credentials | `.env` | K8s Secrets (Sealed) |
| AWS credentials | Never in code | IAM Roles (IRSA) |

**Rule** : Never hardcode secrets. Never commit `.env` to Git.
