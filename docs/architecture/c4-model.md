# C4 Model — AI SOC Platform

## Level 1 — System Context

```mermaid
C4Context
    title System Context — AI SOC Platform

    Person(analyst, "SOC Analyst", "Investigates alerts and manages incidents")
    Person(manager, "SOC Manager", "Oversees SOC operations and approves responses")
    Person(admin, "Platform Admin", "Manages platform configuration and users")

    System(soc, "AI SOC Platform", "Collects, detects, correlates security events and provides AI-assisted incident response")

    System_Ext(sources, "Log Sources", "Servers, endpoints, cloud, applications")
    System_Ext(ti, "Threat Intel Feeds", "MISP, AlienVault OTX, commercial feeds")
    System_Ext(idp, "Identity Provider", "Corporate SSO / Keycloak")
    System_Ext(notify, "Notification Channels", "Email, Slack, PagerDuty")

    Rel(sources, soc, "Sends security events", "HTTPS/Syslog/Beats")
    Rel(analyst, soc, "Uses dashboard, investigates", "HTTPS/WSS")
    Rel(manager, soc, "Manages incidents, approves SOAR", "HTTPS")
    Rel(admin, soc, "Administers platform", "HTTPS")
    Rel(soc, ti, "Fetches IOCs and reputation", "HTTPS")
    Rel(soc, idp, "Authenticates users", "OAuth2/OIDC")
    Rel(soc, notify, "Sends alerts and notifications", "SMTP/Webhook")
```

## Level 2 — Container Diagram

```mermaid
C4Container
    title Container Diagram — AI SOC Platform

    Person(analyst, "SOC Analyst")

    Container_Boundary(c1, "AI SOC Platform") {
        Container(fe, "Frontend", "Next.js, React, TypeScript", "SOC Dashboard with real-time updates")
        Container(gw, "API Gateway", "FastAPI", "Routing, auth, rate limiting, WebSocket")
        Container(auth, "Auth Service", "FastAPI", "IAM integration, RBAC, audit")
        Container(coll, "Collector Service", "FastAPI", "Event ingestion and normalization")
        Container(det, "Detection Service", "FastAPI", "Rule-based and ML detection")
        Container(corr, "Correlation Service", "FastAPI", "Event correlation and incident creation")
        Container(ti, "Threat Intel Service", "FastAPI", "IOC management and enrichment")
        Container(inc, "Incident Service", "FastAPI", "Incident lifecycle and SOAR")
        Container(ai, "AI Service", "FastAPI", "RAG, LLM inference, recommendations")
        Container(notif, "Notification Service", "FastAPI", "Multi-channel notifications")

        ContainerDb(pg, "PostgreSQL", "PostgreSQL 16 + pgvector", "Relational data, vectors, incidents")
        ContainerDb(redis, "Redis", "Redis 7", "Cache, rate limits, detection state")
        ContainerDb(os, "OpenSearch", "OpenSearch 2.x", "Event/alert search and analytics")
        ContainerQueue(kafka, "Kafka", "Apache Kafka 3.x", "Event streaming backbone")
        Container(kc, "Keycloak", "Keycloak 24", "Identity, OAuth2, MFA")
        Container(prom, "Prometheus", "Prometheus", "Metrics collection")
        Container(graf, "Grafana", "Grafana", "Dashboards and visualization")
    }

    Rel(analyst, fe, "Uses", "HTTPS")
    Rel(fe, gw, "API calls, WebSocket", "HTTPS/WSS")
    Rel(gw, auth, "Validate token", "REST")
    Rel(gw, inc, "Incident CRUD", "REST")
    Rel(gw, ai, "AI queries", "REST")
    Rel(gw, coll, "Event ingestion", "REST")
    Rel(coll, kafka, "Publish events", "Kafka Protocol")
    Rel(kafka, det, "Consume events", "Kafka Protocol")
    Rel(kafka, corr, "Consume alerts", "Kafka Protocol")
    Rel(det, kafka, "Publish alerts", "Kafka Protocol")
    Rel(corr, inc, "Create incidents", "REST")
    Rel(inc, ai, "Request analysis", "REST")
    Rel(kafka, notif, "Consume critical alerts", "Kafka Protocol")
    Rel(det, os, "Index alerts", "HTTPS")
    Rel(coll, os, "Index events", "HTTPS")
    Rel(inc, pg, "Persist incidents", "SQL")
    Rel(ai, pg, "Vector search", "SQL")
    Rel(auth, kc, "OAuth2/OIDC", "HTTPS")
    Rel(gw, redis, "Session cache", "Redis Protocol")
```

## Level 3 — Component Diagram (Detection Service)

```mermaid
flowchart TB
    subgraph DetectionService["detection-service"]
        subgraph API["API Layer"]
            ROUTES[FastAPI Routes]
            MIDDLEWARE[Auth Middleware]
        end

        subgraph Core["Detection Core"]
            RULE_ENGINE[Rule Engine]
            SIGMA[Sigma Parser]
            THRESHOLD[Threshold Detector]
            BEHAVIORAL[Behavioral Analyzer]
            ML[ML Anomaly Detector<br/>Isolation Forest]
        end

        subgraph Infra["Infrastructure"]
            KAFKA_CONSUMER[Kafka Consumer]
            KAFKA_PRODUCER[Kafka Producer]
            OS_CLIENT[OpenSearch Client]
            REDIS_STATE[Redis State Store]
            METRICS[Prometheus Metrics]
        end

        subgraph Domain["Domain"]
            ALERT_FACTORY[Alert Factory]
            MITRE_MAPPER[MITRE Mapper]
        end
    end

    KAFKA_CONSUMER --> RULE_ENGINE
    KAFKA_CONSUMER --> SIGMA
    KAFKA_CONSUMER --> THRESHOLD
    KAFKA_CONSUMER --> BEHAVIORAL
    KAFKA_CONSUMER --> ML

    RULE_ENGINE --> ALERT_FACTORY
    SIGMA --> ALERT_FACTORY
    THRESHOLD --> REDIS_STATE
    THRESHOLD --> ALERT_FACTORY
    BEHAVIORAL --> ALERT_FACTORY
    ML --> ALERT_FACTORY

    ALERT_FACTORY --> MITRE_MAPPER
    MITRE_MAPPER --> KAFKA_PRODUCER
    MITRE_MAPPER --> OS_CLIENT
    ALERT_FACTORY --> METRICS
```

## Level 3 — Component Diagram (AI Service)

```mermaid
flowchart TB
    subgraph AIService["ai-service"]
        subgraph API["API Layer"]
            AI_ROUTES[FastAPI Routes<br/>analyze, summarize, explain, recommend]
        end

        subgraph RAG["RAG Pipeline"]
            EMBED[Embedding Service<br/>HuggingFace]
            RETRIEVER[Vector Retriever<br/>pgvector]
            RERANKER[Context Reranker]
            LLM[LLM Gateway<br/>OpenAI-compatible]
            PROMPT[Prompt Templates]
        end

        subgraph Knowledge["Knowledge Base"]
            MITRE_KB[MITRE ATT&CK]
            CVE_KB[CVE Database]
            OWASP_KB[OWASP Docs]
            INCIDENT_KB[Past Incidents]
            TI_KB[Threat Intel]
            SOC_DOCS[Internal SOC Docs]
        end

        subgraph ML["ML Module"]
            ANOMALY[Anomaly Detection]
            FEATURE[Feature Extractor]
        end
    end

    AI_ROUTES --> EMBED
    EMBED --> RETRIEVER
    RETRIEVER --> RERANKER
    RERANKER --> PROMPT
    PROMPT --> LLM

    Knowledge --> RETRIEVER
    AI_ROUTES --> ANOMALY
    ANOMALY --> FEATURE
```

## Deployment Diagram

```mermaid
flowchart TB
    subgraph Internet
        USER[SOC Analyst Browser]
    end

    subgraph AWS["AWS Cloud"]
        subgraph VPC
            ALB[Application Load Balancer<br/>TLS termination]

            subgraph EKS["Amazon EKS Cluster"]
                subgraph NS_Frontend["namespace: frontend"]
                    FE_POD[frontend Deployment<br/>replicas: 2]
                end

                subgraph NS_Gateway["namespace: gateway"]
                    GW_POD[api-gateway Deployment<br/>replicas: 3, HPA]
                end

                subgraph NS_Services["namespace: services"]
                    AUTH_POD[auth-service]
                    COLL_POD[collector-service<br/>replicas: 3, HPA]
                    DET_POD[detection-service<br/>replicas: 3, HPA]
                    CORR_POD[correlation-service]
                    TI_POD[threat-intelligence-service]
                    INC_POD[incident-service]
                    AI_POD[ai-service<br/>GPU node optional]
                    NOTIF_POD[notification-service]
                end

                subgraph NS_Infra["namespace: infrastructure"]
                    KC_POD[Keycloak]
                    KAFKA_POD[Strimzi Kafka]
                    OS_POD[OpenSearch Operator]
                    PROM_POD[Prometheus]
                    GRAF_POD[Grafana]
                end

                INGRESS[Ingress Controller<br/>nginx/ALB]
            end

            subgraph Managed["AWS Managed Services"]
                RDS[(RDS PostgreSQL<br/>Multi-AZ)]
                ELASTICACHE[(ElastiCache Redis)]
                S3[(S3<br/>backups, ML models)]
                SECRETS[Secrets Manager]
                CW[CloudWatch]
            end
        end
    end

    USER --> ALB
    ALB --> INGRESS
    INGRESS --> FE_POD
    INGRESS --> GW_POD
    GW_POD --> NS_Services
    NS_Services --> RDS
    NS_Services --> ELASTICACHE
    NS_Services --> KAFKA_POD
    NS_Services --> OS_POD
    NS_Services --> SECRETS
    PROM_POD --> CW
```

## Sequence Diagram — Authentication Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as SOC Analyst
    participant FE as Next.js Frontend
    participant GW as API Gateway
    participant KC as Keycloak
    participant AUTH as Auth Service
    participant PG as PostgreSQL

    User->>FE: Access /dashboard
    FE->>FE: Check session (no token)
    FE->>KC: Redirect to /auth (OAuth2 Authorization Code + PKCE)
    User->>KC: Enter credentials + MFA
    KC->>FE: Authorization code
    FE->>KC: Exchange code for tokens (access + refresh)
    KC->>FE: JWT access_token + refresh_token
    FE->>FE: Store tokens (httpOnly cookie / secure storage)

    User->>FE: Navigate to /incidents
    FE->>GW: GET /api/v1/incidents (Bearer JWT)
    GW->>AUTH: POST /internal/validate-token
    AUTH->>KC: Introspect token / JWKS verify
    KC->>AUTH: Token valid + claims
    AUTH->>PG: Log audit event
    AUTH->>GW: User + roles + permissions
    GW->>GW: RBAC check (SOC_ANALYST)
    GW->>GW: Forward to incident-service
    GW->>FE: 200 Incidents list
    FE->>User: Render dashboard
```

## Sequence Diagram — SOAR Response (Simulated)

```mermaid
sequenceDiagram
    autonumber
    actor Analyst as SOC Analyst
    participant FE as Frontend
    participant GW as API Gateway
    participant INC as Incident Service
    participant KAFKA as Kafka
    participant NOTIF as Notification Service
    participant AUDIT as Audit Log

    Analyst->>FE: Click "Block IP" on incident
    FE->>GW: POST /api/v1/incidents/{id}/response-actions
    Note over GW: RBAC: SOC_ANALYST can simulate<br/>SOC_MANAGER required for real execution

    GW->>INC: Create response action
    INC->>INC: approval_required = true
    INC->>INC: simulation_mode = true (default)
    INC->>INC: Simulate BLOCK_IP action
    INC->>KAFKA: Publish to response-actions topic
    INC->>AUDIT: Log action (who, what, when, simulated)
    INC->>FE: 202 Action queued (simulated)

    KAFKA->>NOTIF: Consume response-action
    NOTIF->>NOTIF: Send webhook notification
    NOTIF->>AUDIT: Log notification delivery

    Note over Analyst: Manager approves for real execution (future)
    Analyst->>FE: View action result in incident timeline
```
