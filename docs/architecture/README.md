# AI SOC Platform — Architecture Overview

> **Phase 1** — Document d'architecture. Aucun code microservice à ce stade.

## Table des matières

1. [Vision et objectifs](#1-vision-et-objectifs)
2. [Architecture globale](#2-architecture-globale)
3. [Microservices](#3-microservices)
4. [Communications synchrones vs asynchrones](#4-communications)
5. [Modèle de données (aperçu)](#5-modèle-de-données)
6. [Sécurité](#6-sécurité)
7. [Observabilité](#7-observabilité)
8. [Documents associés](#8-documents-associés)

---

## 1. Vision et objectifs

AI SOC Platform vise à fournir une plateforme SOC **distribuée**, **event-driven**, **observable** et **sécurisée** capable de traiter des millions d'événements par jour tout en offrant une expérience analyste moderne avec assistance IA.

### Principes architecturaux

| Principe | Application |
|----------|-------------|
| **Event-driven** | Kafka comme backbone ; découplage producteur/consommateur |
| **Microservices** | Services indépendants, déployables et scalables séparément |
| **CQRS partiel** | Écriture via Kafka ; lecture via OpenSearch + PostgreSQL |
| **Defense in depth** | IAM, RBAC, MFA, NetworkPolicies, audit |
| **Fail-safe SOAR** | Actions de réponse simulées par défaut |
| **Observable by design** | Métriques Prometheus, logs structurés, traces |
| **AI-augmented** | RAG pour contexte ; ML pour anomalies |

---

## 2. Architecture globale

### Diagramme système (haut niveau)

```mermaid
flowchart TB
    subgraph External["Sources externes"]
        AGENTS[Agents / Beats / Syslog]
        CLOUD[Cloud APIs<br/>AWS/Azure/GCP]
        APPS[Applications]
        TI_FEEDS[TI Feeds<br/>MISP, OTX]
    end

    subgraph Users["Utilisateurs"]
        ANALYST[SOC Analyst]
        MANAGER[SOC Manager]
        ADMIN[Platform Admin]
    end

    subgraph Frontend["Frontend Layer"]
        DASH[Next.js Dashboard<br/>WebSocket + REST]
    end

    subgraph Gateway["API Layer"]
        GW[API Gateway<br/>FastAPI]
    end

    subgraph Services["Microservices"]
        AUTH[Auth Service]
        COLL[Collector Service]
        DET[Detection Service]
        CORR[Correlation Service]
        TI[Threat Intel Service]
        INC[Incident Service]
        AI[AI Service]
        NOTIF[Notification Service]
    end

    subgraph Streaming["Event Streaming"]
        KAFKA[(Apache Kafka)]
    end

    subgraph Storage["Data Layer"]
        PG[(PostgreSQL<br/>+ pgvector)]
        REDIS[(Redis)]
        OS[(OpenSearch)]
    end

    subgraph Identity["Identity"]
        KC[Keycloak<br/>OAuth2/OIDC]
    end

    subgraph Observability["Observability"]
        PROM[Prometheus]
        GRAF[Grafana]
    end

    AGENTS --> COLL
    CLOUD --> COLL
    APPS --> COLL

    ANALYST --> DASH
    MANAGER --> DASH
    ADMIN --> DASH

    DASH <-->|WebSocket/REST| GW
    GW --> AUTH
    GW --> INC
    GW --> AI
    GW --> TI
    GW --> DET

    AUTH --> KC
    COLL --> KAFKA
    KAFKA --> DET
    KAFKA --> CORR
    KAFKA --> TI
    KAFKA --> NOTIF

    DET --> KAFKA
    CORR --> KAFKA
    CORR --> INC
    INC --> PG
    DET --> OS
    COLL --> OS
    AI --> PG
    AI --> REDIS
    TI --> PG

    GW --> REDIS
    Services --> PROM
    PROM --> GRAF
    TI_FEEDS --> TI
```

### Flux de données principal

```mermaid
sequenceDiagram
    autonumber
    participant Source as Event Source
    participant Collector as Collector Service
    participant Kafka as Kafka
    participant Detection as Detection Engine
    participant OpenSearch as OpenSearch
    participant Correlation as Correlation Engine
    participant Incident as Incident Service
    participant AI as AI Service
    participant WS as WebSocket
    participant Dashboard as SOC Dashboard

    Source->>Collector: POST /api/v1/events
    Collector->>Collector: Validate & Normalize
    Collector->>Kafka: security-events
    Collector->>OpenSearch: Index event

    Kafka->>Detection: Consume event
    Detection->>Detection: Rule / ML / Sigma
    alt Alert triggered
        Detection->>Kafka: alerts
        Detection->>OpenSearch: Index alert
        Kafka->>Correlation: Consume alert
        Correlation->>Correlation: Chain analysis
        alt Incident created
            Correlation->>Incident: Create incident
            Incident->>AI: Request analysis
            AI->>Incident: AI summary + recommendations
            Incident->>WS: Push update
            WS->>Dashboard: Real-time notification
        end
    end
```

---

## 3. Microservices

### Vue d'ensemble des services

```mermaid
graph LR
    subgraph Ingress
        GW[API Gateway]
    end

    subgraph Core
        AUTH[auth-service<br/>:8001]
        COLL[collector-service<br/>:8002]
        DET[detection-service<br/>:8003]
        CORR[correlation-service<br/>:8004]
        TI[threat-intelligence-service<br/>:8005]
        INC[incident-service<br/>:8006]
        AI[ai-service<br/>:8007]
        NOTIF[notification-service<br/>:8008]
    end

    GW --> AUTH
    GW --> COLL
    GW --> INC
    GW --> AI
    GW --> TI

    COLL --> KAFKA
    DET --> KAFKA
    CORR --> KAFKA
    NOTIF --> KAFKA
```

### Responsabilités par service

| Service | Port | Responsabilités | Base de données |
|---------|------|-----------------|-----------------|
| **api-gateway** | 8000 | Routing, rate limiting, auth validation, aggregation | Redis (cache, sessions) |
| **auth-service** | 8001 | Proxy IAM, permissions, audit auth, session mgmt | PostgreSQL |
| **collector-service** | 8002 | Ingestion, validation, normalisation, publication Kafka | OpenSearch (write) |
| **detection-service** | 8003 | Rules, Sigma, threshold, behavioral, ML anomaly | OpenSearch (read), Redis (state) |
| **correlation-service** | 8004 | Event chaining, incident auto-creation, timeline | PostgreSQL, OpenSearch |
| **threat-intelligence-service** | 8005 | IOC mgmt, reputation, TI feeds, enrichment | PostgreSQL |
| **incident-service** | 8006 | CRUD incidents, workflow, assignment, SOAR | PostgreSQL |
| **ai-service** | 8007 | RAG, LLM inference, embeddings, recommendations | PostgreSQL (pgvector) |
| **notification-service** | 8008 | Email, webhook, Slack/Discord alerts | PostgreSQL (delivery log) |

### Détail : Collector Service

```
Responsabilités :
├── POST /api/v1/events          → Ingestion multi-format
├── POST /api/v1/events/bulk     → Ingestion batch
├── Validation Pydantic
├── Normalisation ECS-like schema
├── Génération event_id (UUID v7)
├── Enrichissement metadata (received_at, source_type)
├── Publication Kafka (topic routing by event_type)
└── Indexation OpenSearch async
```

### Détail : Detection Engine

```
Modes de détection :
├── A. Rule-based (custom JSON rules)
├── B. Sigma rules (pySigma)
├── C. Threshold (sliding window, Redis)
├── D. Behavioral (baseline deviation)
└── E. Anomaly (Isolation Forest, scikit-learn)

Output :
├── Alert → Kafka topic "alerts"
├── Index OpenSearch "alerts"
└── Métriques Prometheus
```

### Détail : Correlation Engine

```
Stratégies :
├── Temporal correlation (time window)
├── Entity correlation (IP, user, host)
├── Attack chain templates (MITRE-based)
└── Graph-based event linking

Output :
├── Incident auto-creation
├── Risk score calculation
├── MITRE technique mapping
└── Timeline generation
```

---

## 4. Communications

### Synchrones (REST/gRPC)

```mermaid
graph TD
    FE[Frontend] -->|HTTPS REST| GW[API Gateway]
    GW -->|REST + JWT| AUTH[Auth Service]
    GW -->|REST| INC[Incident Service]
    GW -->|REST| AI[AI Service]
    GW -->|REST| TI[Threat Intel Service]
    GW -->|REST| COLL[Collector Service]
    GW -->|REST| DET[Detection Service]

    CORR[Correlation] -->|REST| INC
    CORR -->|REST| TI
    DET -->|REST| TI
    INC -->|REST| AI
    INC -->|REST| AUTH
```

| Appelant | Appelé | Endpoint | Usage |
|----------|--------|----------|-------|
| Frontend | API Gateway | `/api/v1/*` | Toutes les opérations UI |
| API Gateway | Auth Service | `/internal/validate-token` | Validation JWT |
| API Gateway | Auth Service | `/internal/permissions` | RBAC check |
| Correlation | Incident Service | `POST /internal/incidents` | Auto-création incident |
| Correlation | Threat Intel | `GET /internal/ioc/lookup` | Enrichissement IOC |
| Detection | Threat Intel | `GET /internal/reputation/{ip}` | IP reputation |
| Incident | AI Service | `POST /internal/analyze` | Analyse IA |
| Frontend | API Gateway | `WS /ws/alerts` | Temps réel |

### Asynchrones (Kafka)

Voir [Kafka Architecture](kafka-architecture.md) pour le détail complet.

| Topic | Producteurs | Consommateurs |
|-------|-------------|---------------|
| `security-events` | collector-service | detection, correlation, opensearch-indexer |
| `authentication-events` | collector-service | detection, correlation |
| `network-events` | collector-service | detection, correlation |
| `application-events` | collector-service | detection |
| `cloud-events` | collector-service | detection, correlation |
| `alerts` | detection-service | correlation, notification, opensearch-indexer |
| `incidents` | correlation-service, incident-service | notification, ai-service |
| `response-actions` | incident-service | notification, audit |

---

## 5. Modèle de données

Aperçu ERD — voir [Data Architecture](data-architecture.md) pour le schéma complet.

```mermaid
erDiagram
    User ||--o{ AuditLog : generates
    User }o--|| Role : has
    Role ||--o{ Permission : grants

    Event ||--o{ Alert : triggers
    Alert ||--o{ Incident : correlates_to
    Incident ||--o{ ResponseAction : has
    Incident ||--o{ AIAnalysis : has
    Incident }o--o{ IOC : contains
    Incident }o--o{ MITRETechnique : maps_to

    Alert }o--o{ MITRETechnique : maps_to
    DetectionRule ||--o{ Alert : produces

    Asset ||--o{ Event : source
    ThreatIntelligence ||--o{ IOC : defines

    User {
        uuid id PK
        string keycloak_id UK
        string email
        string username
        uuid role_id FK
        boolean mfa_enabled
        timestamp last_login
    }

    Event {
        uuid event_id PK
        timestamp timestamp
        string source
        string event_type
        string action
        string status
        jsonb raw_data
        jsonb normalized_data
        string source_ip
        string username
        string correlation_id
    }

    Alert {
        uuid alert_id PK
        string type
        string severity
        float confidence
        string source_ip
        uuid[] related_events
        timestamp created_at
    }

    Incident {
        uuid id PK
        string incident_number UK
        string title
        text description
        string severity
        int risk_score
        float confidence
        enum status
        uuid assigned_analyst FK
        jsonb timeline
        jsonb ai_analysis
        timestamp created_at
    }

    IOC {
        uuid id PK
        enum ioc_type
        string value UK
        int risk_score
        enum classification
        enum confidence
        timestamp first_seen
        timestamp last_seen
    }

    MITRETechnique {
        string technique_id PK
        string name
        string tactic
        string sub_technique
        text description
    }
```

---

## 6. Sécurité

Voir [Threat Model](../security/threat-model.md) pour l'analyse STRIDE complète.

### Modèle de sécurité (résumé)

```mermaid
flowchart TB
    subgraph Perimeter
        WAF[WAF / Rate Limiting]
        TLS[TLS 1.3]
    end

    subgraph Identity
        KC[Keycloak]
        MFA[MFA TOTP]
        RBAC[RBAC]
    end

    subgraph Application
        JWT[JWT Validation]
        AUDIT[Audit Logging]
        INPUT[Input Validation]
    end

    subgraph Network
        NP[NetworkPolicies K8s]
        MTLS[mTLS inter-services]
    end

    subgraph Data
        ENC[Encryption at rest]
        SECRETS[Secrets Manager]
        LEAST[Least Privilege DB]
    end

    WAF --> TLS --> KC
    KC --> MFA --> RBAC
    RBAC --> JWT --> AUDIT
    JWT --> INPUT
    NP --> MTLS
    ENC --> SECRETS --> LEAST
```

### Rôles RBAC

| Rôle | Permissions |
|------|-------------|
| **ADMIN** | Full platform access, user mgmt, config |
| **SOC_MANAGER** | Incidents, rules, reports, approve SOAR actions |
| **SOC_ANALYST** | View/create incidents, run AI, simulate SOAR |
| **VIEWER** | Read-only dashboard, events, incidents |

---

## 7. Observabilité

```mermaid
flowchart LR
    subgraph Services
        S1[All Microservices]
    end

    subgraph Metrics
        PROM[Prometheus]
        GRAF[Grafana Dashboards]
    end

    subgraph Logs
        OS_LOG[OpenSearch Logs Index]
    end

    subgraph Traces
        OTEL[OpenTelemetry<br/>future phase]
    end

    S1 -->|/metrics| PROM
    PROM --> GRAF
    S1 -->|structured JSON| OS_LOG
    S1 -.-> OTEL
```

### Métriques clés

| Métrique | Type | Service |
|----------|------|---------|
| `api_requests_total` | Counter | api-gateway |
| `api_latency_seconds` | Histogram | api-gateway |
| `events_processed_total` | Counter | collector, detection |
| `events_per_second` | Gauge | collector |
| `alerts_created_total` | Counter | detection |
| `incidents_created_total` | Counter | correlation, incident |
| `detection_latency_seconds` | Histogram | detection |
| `ai_inference_time_seconds` | Histogram | ai-service |
| `kafka_consumer_lag` | Gauge | all consumers |

---

## 8. Documents associés

| Document | Contenu |
|----------|---------|
| [C4 Model](c4-model.md) | Context, Container, Component diagrams |
| [Data Architecture](data-architecture.md) | ERD complet, schémas JSON, index OpenSearch |
| [Kafka Architecture](kafka-architecture.md) | Topics, partitions, DLQ, idempotency |
| [AI/RAG Architecture](ai-rag-architecture.md) | Pipeline RAG, embeddings, LLM |
| [Technical Decisions](technical-decisions.md) | ADR-001 à ADR-010 |
| [Roadmap](roadmap.md) | 26 phases détaillées |
| [Threat Model](../security/threat-model.md) | STRIDE, mitigations |
| [Deployment](../deployment/deployment-overview.md) | Docker, K8s, AWS |
