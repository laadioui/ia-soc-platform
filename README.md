# AI SOC Platform

**AI-Powered Security Operations Center** — Plateforme SOC moderne, cloud-native et event-driven.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-15-black)](https://nextjs.org/)

## Project Overview

AI SOC Platform est une plateforme de Security Operations Center (SOC) conçue pour :

- Collecter et normaliser des événements de sécurité multi-sources
- Détecter et corréler des comportements suspects en temps réel
- Calculer des risk scores et enrichir avec MITRE ATT&CK / Threat Intelligence
- Gérer des incidents et proposer des réponses contrôlées (SOAR)
- Fournir un assistant IA basé sur RAG pour les analystes SOC

## Status

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Architecture | ✅ Complete |
| 2 | Infrastructure locale (Docker Compose) | ⏳ Pending |
| 3 | IAM (Keycloak) | ⏳ Pending |
| 4+ | Microservices & features | ⏳ Pending |

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | Next.js, React, TypeScript, Tailwind, shadcn/ui, Recharts, WebSocket, TanStack Query |
| Backend | Python 3.12+, FastAPI, Pydantic, SQLAlchemy, Alembic |
| Databases | PostgreSQL, Redis, OpenSearch, pgvector |
| Streaming | Apache Kafka |
| Identity | Keycloak, OAuth2/OIDC, JWT, RBAC, MFA |
| AI/ML | PyTorch, Hugging Face, scikit-learn, RAG, pgvector |
| Infra | Docker, Kubernetes, Helm, Terraform, AWS |
| Observability | Prometheus, Grafana |
| DevSecOps | GitHub Actions, ArgoCD, Semgrep, Trivy, Gitleaks, OWASP ZAP |

## Architecture

```
                    SOC ANALYST
                         |
                         v
                 Next.js Dashboard
                         |
                         v
                    API Gateway (FastAPI)
                         |
       +-----------------+-----------------+
       |                 |                 |
       v                 v                 v
   IAM Service      Incident Service    AI Service
       |                 |                 |
       +-----------------+-----------------+
                         |
                         v
                       Kafka
                         |
        +----------------+----------------+
        |                |                |
        v                v                v
 Detection Engine  Correlation Engine  Threat Intel
        |                |                |
        +----------------+----------------+
                         |
                         v
                     OpenSearch
                         |
                         v
                    PostgreSQL
```

Documentation complète : [`docs/architecture/`](docs/architecture/)

## Repository Structure

```
ai-soc-platform/
├── apps/
│   ├── frontend/              # Next.js SOC Dashboard
│   └── api-gateway/             # FastAPI API Gateway
├── services/
│   ├── auth-service/
│   ├── collector-service/
│   ├── detection-service/
│   ├── correlation-service/
│   ├── threat-intelligence-service/
│   ├── incident-service/
│   ├── ai-service/
│   └── notification-service/
├── infrastructure/
│   ├── docker/
│   ├── kubernetes/
│   ├── helm/
│   └── terraform/
├── detection-rules/
│   ├── sigma/
│   ├── yara/
│   └── custom/
├── ml/
├── tests/
├── docs/
├── scripts/
└── .github/workflows/
```

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture Overview](docs/architecture/README.md) | Vue d'ensemble et diagrammes |
| [C4 Model](docs/architecture/c4-model.md) | Context, Container, Component |
| [Data Architecture](docs/architecture/data-architecture.md) | ERD, schémas, persistence |
| [Kafka Architecture](docs/architecture/kafka-architecture.md) | Topics, consumers, DLQ |
| [AI/RAG Architecture](docs/architecture/ai-rag-architecture.md) | Pipeline IA et RAG |
| [Threat Model](docs/security/threat-model.md) | Modèle de menaces STRIDE |
| [Technical Decisions](docs/architecture/technical-decisions.md) | ADR et choix techniques |
| [Roadmap](docs/architecture/roadmap.md) | Plan de développement par phases |
| [Deployment](DEPLOYMENT.md) | Déploiement gratuit permanent : Vercel + Render |

## Getting Started

```bash
# Backend (FastAPI) — avec données de démo auto-injectées
cd services/collector-service
pip install -r requirements.txt
SEED_DEMO_DATA=true uvicorn app.main:app --port 8000

# Frontend (Next.js)
cd apps/frontend
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1 npm run dev
```

Comptes de démonstration : `socadmin / AdminPass123!` — `analyst / Analyst@2026!`

## 🌐 Démo en ligne (gratuit, permanent)

- **Application** : https://ia-soc-platform.vercel.app — responsive téléphone / tablette / PC
- **API** : https://ai-soc-platform-api.vercel.app (docs : [/docs](https://ai-soc-platform-api.vercel.app/docs), health : `/health`)

Hébergement gratuit sur Vercel : frontend Next.js + backend FastAPI en fonction
Python serverless (SQLite en `/tmp` avec réinjection automatique des données
de démo à chaque cold start via `SEED_DEMO_DATA=true`). Interface adaptée aux
mobiles (tiroir de navigation) depuis août 2026. Voir [DEPLOYMENT.md](DEPLOYMENT.md)
pour l'architecture cible Render + Vercel et les alternatives.

## Security

- OWASP Top 10 compliance
- RBAC avec Keycloak
- MFA obligatoire pour les rôles sensibles
- Secrets via variables d'environnement / AWS Secrets Manager
- Audit logging complet
- Actions SOAR simulées par défaut

## License

MIT — Voir [LICENSE](LICENSE)
