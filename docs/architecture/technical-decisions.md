# Technical Decisions (ADR) — AI SOC Platform

> Architecture Decision Records — Décisions techniques clés et leur justification.

---

## ADR-001 : Architecture Event-Driven avec Kafka

**Status** : Accepted

**Contexte** : La plateforme doit traiter des volumes élevés d'événements de sécurité en temps réel, avec plusieurs consommateurs indépendants (detection, correlation, indexing, notification).

**Décision** : Utiliser Apache Kafka comme backbone event-driven.

**Alternatives considérées** :
| Option | Pour | Contre |
|--------|------|--------|
| RabbitMQ | Simple, bon pour task queues | Moins adapté au replay, au throughput élevé |
| Redis Streams | Faible latence, déjà dans le stack | Durabilité limitée, pas de replay natif |
| AWS Kinesis | Managed, scalable | Vendor lock-in, coût, complexité local dev |
| **Apache Kafka** | Throughput, replay, ecosystem, Strimzi K8s | Complexité ops, ressources dev |

**Justification** : Kafka offre le meilleur compromis entre throughput, durabilité, replay capability et écosystème K8s (Strimzi). Le mode KRaft simplifie le déploiement dev (sans Zookeeper).

---

## ADR-002 : Polyglot Persistence

**Status** : Accepted

**Contexte** : Différents types de données avec des patterns d'accès différents.

**Décision** :
- **PostgreSQL** : données relationnelles (incidents, users, IOC, audit)
- **OpenSearch** : events, alerts, full-text search, aggregations
- **Redis** : cache, rate limiting, detection state
- **pgvector** : embeddings RAG

**Justification** : Chaque store est optimisé pour son use case. OpenSearch excelle en search/analytics time-series. PostgreSQL garantit l'intégrité relationnelle. pgvector évite un vector DB séparé (Pinecone, Weaviate) en dev.

---

## ADR-003 : Keycloak pour IAM

**Status** : Accepted

**Contexte** : Besoin d'authentification enterprise-grade avec OAuth2/OIDC, MFA, RBAC.

**Décision** : Keycloak comme Identity Provider.

**Alternatives** :
| Option | Pour | Contre |
|--------|------|--------|
| Auth0 | Managed, simple | Coût, vendor lock-in |
| Custom JWT | Contrôle total | Réinventer la roue, MFA complexe |
| **Keycloak** | Open source, OIDC, MFA, RBAC, self-hosted | Ressources, courbe d'apprentissage |

**Justification** : Keycloak est le standard open source pour IAM enterprise. Self-hosted = pas de vendor lock-in. Supporte OIDC, SAML, MFA TOTP, fine-grained RBAC.

---

## ADR-004 : FastAPI pour tous les microservices backend

**Status** : Accepted

**Contexte** : Besoin d'un framework Python async, performant, avec validation et OpenAPI auto-généré.

**Décision** : FastAPI pour api-gateway et tous les microservices.

**Justification** :
- Async natif (compatible Kafka consumers, HTTP concurrent)
- Pydantic intégré (validation, serialization)
- OpenAPI/Swagger auto-généré
- Performance comparable à Node.js/Go
- Écosystème Python pour ML (scikit-learn, PyTorch, HuggingFace)
- Typing strict avec mypy

---

## ADR-005 : Next.js App Router pour le frontend

**Status** : Accepted

**Contexte** : Dashboard SOC moderne avec SSR, routing, WebSocket.

**Décision** : Next.js 15 avec App Router, TypeScript, Tailwind CSS, shadcn/ui.

**Justification** :
- SSR pour les pages initiales (performance)
- App Router pour le routing moderne
- shadcn/ui : composants accessibles, customisables, professionnels
- TanStack Query pour le data fetching/caching
- Recharts pour les graphiques SOC
- Écosystème React mature

---

## ADR-006 : Schema-per-Service (PostgreSQL)

**Status** : Accepted

**Contexte** : Plusieurs microservices ont besoin de PostgreSQL. Faut-il une DB par service ou un schéma partagé ?

**Décision** : Un cluster PostgreSQL, un schema par service (`auth`, `incidents`, `ti`, `detection`, `ai`), plus un schema `shared` pour les tables communes (MITRE, assets).

**Justification** :
- Simplifie le dev local (un seul PostgreSQL)
- Isole les services logiquement
- Migration path vers DB-per-service en prod si nécessaire
- pgvector accessible depuis le schema `ai`

---

## ADR-007 : SOAR Simulation Mode par défaut

**Status** : Accepted

**Contexte** : Les actions de réponse (BLOCK_IP, DISABLE_USER, etc.) peuvent être destructives.

**Décision** : Toutes les actions SOAR sont **simulées par défaut** (`simulation_mode=true`). L'exécution réelle nécessite `approval_required=true` + rôle SOC_MANAGER.

**Justification** : Évite les dommages accidentels en dev/staging. Permet la démonstration du workflow complet sans risque. Conforme aux bonnes pratiques SOAR (human-in-the-loop).

---

## ADR-008 : Monorepo

**Status** : Accepted

**Contexte** : Organisation du code pour 8+ microservices, frontend, infra, ML, tests.

**Décision** : Monorepo avec structure `apps/`, `services/`, `infrastructure/`, etc.

**Justification** :
- Visibilité globale de l'architecture
- CI/CD unifié
- Partage de types/schemas entre services
- Idéal pour un projet portfolio
- Makefile centralisé pour les opérations communes

---

## ADR-009 : JSON Schema pour les events Kafka (pas Avro/Protobuf)

**Status** : Accepted

**Contexte** : Besoin de schema evolution pour les messages Kafka.

**Décision** : JSON avec `schema_version` dans l'envelope, JSON Schema files pour validation.

**Alternatives** :
| Option | Pour | Contre |
|--------|------|--------|
| Avro + Schema Registry | Compact, evolution strict | Complexité dev, schema registry à opérer |
| Protobuf | Performance, typing | Moins lisible en debug, tooling |
| **JSON + JSON Schema** | Lisible, simple, debug friendly | Plus verbose, pas de binary |

**Justification** : En phase dev/portfolio, la lisibilité et la simplicité priment. JSON est natif Python/JS. Migration vers Avro possible en prod si le volume le justifie.

---

## ADR-010 : Ollama (dev) / OpenAI-compatible API (prod) pour LLM

**Status** : Accepted

**Contexte** : Le RAG/AI assistant nécessite un LLM. Coût et privacy sont des contraintes.

**Décision** :
- **Dev** : Ollama local avec `llama3.1:8b` (gratuit, offline)
- **Prod** : API OpenAI-compatible (OpenAI, Azure OpenAI, ou vLLM self-hosted)

**Justification** : Ollama permet le dev/test sans coût API. L'abstraction LLM Gateway permet de switcher de provider. vLLM self-hosted en option pour la privacy.

---

## ADR-011 : Isolation Forest pour Anomaly Detection (Phase 1 ML)

**Status** : Accepted

**Contexte** : Premier modèle ML pour la détection d'anomalies. Besoin d'un modèle unsupervised (pas de labels).

**Décision** : Isolation Forest (scikit-learn) comme modèle initial.

**Justification** :
- Unsupervised : pas besoin de labels
- Rapide à entraîner et inférer (<15ms)
- Interprétable (feature contribution)
- scikit-learn : stable, bien documenté
- Upgrade path vers PyTorch autoencoder

---

## ADR-012 : ECS-inspired Event Normalization

**Status** : Accepted

**Contexte** : Events provenant de sources hétérogènes (Linux, Windows, cloud, apps).

**Décision** : Normalisation inspirée d'Elastic Common Schema (ECS) avec champs custom.

**Justification** : ECS est un standard de facto dans l'industrie SIEM. Facilite l'intégration future avec Elastic/Splunk. Champs custom pour les extensions AI SOC.

---

## ADR-013 : WebSocket via API Gateway

**Status** : Accepted

**Contexte** : Le dashboard SOC nécessite des mises à jour temps réel (alertes, incidents).

**Décision** : WebSocket endpoint sur l'API Gateway (`/ws/alerts`, `/ws/incidents`). Le gateway consomme Kafka et push aux clients connectés.

**Justification** :
- Point d'entrée unique (pas de WebSocket par service)
- Auth JWT sur le handshake WebSocket
- Redis pour tracker les connexions actives
- Kafka → Gateway → WebSocket = decoupled

---

## ADR-014 : Prometheus + Grafana (pas ELK pour metrics)

**Status** : Accepted

**Contexte** : Besoin d'observabilité metrics + logs.

**Décision** :
- **Metrics** : Prometheus + Grafana
- **Logs** : Structured JSON → OpenSearch (index `platform-logs`)
- **Traces** : OpenTelemetry (future phase)

**Justification** : Prometheus est le standard K8s pour les metrics. OpenSearch déjà dans le stack pour les events → réutilisation pour les logs. Evite la complexité d'un stack ELK séparé.

---

## ADR-015 : GitHub Actions + ArgoCD pour CI/CD

**Status** : Accepted

**Contexte** : Pipeline DevSecOps avec lint, test, scan, build, deploy.

**Décision** :
- **CI** : GitHub Actions (lint → test → SAST → build → scan → integration test)
- **CD** : ArgoCD (GitOps, sync K8s manifests depuis Git)

**Justification** : GitHub Actions intégré au repo. ArgoCD = GitOps best practice pour K8s. Séparation CI (build) / CD (deploy).

---

## Stack Summary

| Composant | Choix | ADR |
|-----------|-------|-----|
| Event Streaming | Apache Kafka (KRaft) | ADR-001 |
| Databases | PostgreSQL + OpenSearch + Redis + pgvector | ADR-002 |
| IAM | Keycloak | ADR-003 |
| Backend Framework | FastAPI | ADR-004 |
| Frontend | Next.js 15 + shadcn/ui | ADR-005 |
| DB Strategy | Schema-per-service | ADR-006 |
| SOAR | Simulation by default | ADR-007 |
| Repo Structure | Monorepo | ADR-008 |
| Event Schema | JSON + JSON Schema | ADR-009 |
| LLM | Ollama (dev) / OpenAI API (prod) | ADR-010 |
| ML Model | Isolation Forest | ADR-011 |
| Event Normalization | ECS-inspired | ADR-012 |
| Real-time | WebSocket via Gateway | ADR-013 |
| Observability | Prometheus + Grafana | ADR-014 |
| CI/CD | GitHub Actions + ArgoCD | ADR-015 |
