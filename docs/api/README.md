# API Documentation — AI SOC Platform

> Toutes les API sont documentées automatiquement via **OpenAPI 3.1** (Swagger UI).
> Base URL : `http://localhost:8000/api/v1`

## Authentication

Toutes les API (sauf `/health`) requièrent un **Bearer JWT** obtenu via Keycloak OAuth2/OIDC.

```
Authorization: Bearer <access_token>
```

### Auth Endpoints (via Keycloak + auth-service)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/auth/login` | Login (redirect Keycloak) | Public |
| POST | `/api/v1/auth/logout` | Logout + invalidate session | Bearer |
| POST | `/api/v1/auth/refresh` | Refresh access token | Refresh token |
| GET | `/api/v1/auth/me` | Current user profile + roles | Bearer |
| GET | `/api/v1/auth/permissions` | User permissions list | Bearer |

---

## Events (collector-service)

| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| POST | `/api/v1/events` | Ingest single event | API Key / SOC_ANALYST |
| POST | `/api/v1/events/bulk` | Ingest batch (max 1000) | API Key / SOC_ANALYST |
| GET | `/api/v1/events` | Search events | SOC_ANALYST |
| GET | `/api/v1/events/{event_id}` | Get event by ID | SOC_ANALYST |

### POST /api/v1/events

**Request** :
```json
{
  "timestamp": "2026-08-18T00:45:32.123Z",
  "source": "linux-server-01",
  "event_type": "authentication",
  "username": "admin",
  "source_ip": "192.168.1.10",
  "action": "login_failed",
  "status": "failure"
}
```

**Response** `202 Accepted` :
```json
{
  "event_id": "0195a3b2-c4d5-7890-abcd-ef1234567890",
  "status": "accepted",
  "correlation_id": "corr-0195a3b2-abc123"
}
```

**Errors** :
| Code | Description |
|------|-------------|
| 422 | Validation error (invalid fields) |
| 429 | Rate limit exceeded |
| 401 | Unauthorized |

---

## Alerts (detection-service)

| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| GET | `/api/v1/alerts` | List alerts (filterable) | SOC_ANALYST |
| GET | `/api/v1/alerts/{alert_id}` | Get alert detail | SOC_ANALYST |
| PATCH | `/api/v1/alerts/{alert_id}` | Update alert status | SOC_ANALYST |
| GET | `/api/v1/alerts/stats` | Alert statistics | SOC_ANALYST |

### GET /api/v1/alerts

**Query Parameters** :
| Param | Type | Description |
|-------|------|-------------|
| `severity` | string | low, medium, high, critical |
| `status` | string | new, acknowledged, investigating, resolved |
| `alert_type` | string | BRUTE_FORCE, PRIV_ESC, etc. |
| `source_ip` | string | Filter by IP |
| `from` | datetime | Start time range |
| `to` | datetime | End time range |
| `page` | int | Page number (default 1) |
| `size` | int | Page size (default 20, max 100) |

---

## Incidents (incident-service)

| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| POST | `/api/v1/incidents` | Create incident | SOC_ANALYST |
| GET | `/api/v1/incidents` | List incidents | SOC_ANALYST |
| GET | `/api/v1/incidents/{id}` | Get incident detail | SOC_ANALYST |
| PATCH | `/api/v1/incidents/{id}` | Update incident | SOC_ANALYST |
| POST | `/api/v1/incidents/{id}/assign` | Assign analyst | SOC_MANAGER |
| POST | `/api/v1/incidents/{id}/response-actions` | Create SOAR action | SOC_ANALYST |
| GET | `/api/v1/incidents/{id}/timeline` | Get incident timeline | SOC_ANALYST |

### POST /api/v1/incidents

**Request** :
```json
{
  "title": "Suspected Account Compromise",
  "description": "Multiple failed logins followed by privilege escalation",
  "severity": "critical",
  "related_alert_ids": ["alert-001", "alert-002"],
  "related_event_ids": ["evt-001", "evt-002"]
}
```

**Response** `201 Created` :
```json
{
  "id": "uuid-incident-001",
  "incident_number": "INC-2026-00042",
  "title": "Suspected Account Compromise",
  "severity": "critical",
  "risk_score": 87,
  "confidence": 0.91,
  "status": "new",
  "created_at": "2026-08-18T01:00:00.000Z"
}
```

---

## AI (ai-service)

| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| POST | `/api/v1/ai/analyze` | Full incident analysis | SOC_ANALYST |
| POST | `/api/v1/ai/summarize` | Incident summary | SOC_ANALYST |
| POST | `/api/v1/ai/explain-alert` | Explain alert | SOC_ANALYST |
| POST | `/api/v1/ai/recommend-response` | Response recommendations | SOC_ANALYST |
| POST | `/api/v1/ai/chat` | Interactive RAG chat | SOC_ANALYST |

---

## Threat Intelligence (threat-intelligence-service)

| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| GET | `/api/v1/ti/iocs` | List IOCs | SOC_ANALYST |
| POST | `/api/v1/ti/iocs` | Create IOC | SOC_MANAGER |
| GET | `/api/v1/ti/iocs/lookup` | Lookup IOC | SOC_ANALYST |
| GET | `/api/v1/ti/reputation/{type}/{value}` | Get reputation | SOC_ANALYST |

---

## MITRE ATT&CK

| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| GET | `/api/v1/mitre/techniques` | List techniques | VIEWER |
| GET | `/api/v1/mitre/techniques/{id}` | Get technique detail | VIEWER |
| GET | `/api/v1/mitre/tactics` | List tactics | VIEWER |
| GET | `/api/v1/mitre/matrix` | ATT&CK matrix | VIEWER |

---

## Detection Rules

| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| GET | `/api/v1/rules` | List detection rules | SOC_ANALYST |
| POST | `/api/v1/rules` | Create rule | SOC_MANAGER |
| PUT | `/api/v1/rules/{id}` | Update rule | SOC_MANAGER |
| DELETE | `/api/v1/rules/{id}` | Delete rule | SOC_MANAGER |
| POST | `/api/v1/rules/{id}/test` | Test rule against events | SOC_MANAGER |

---

## Dashboard Stats (api-gateway aggregation)

| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| GET | `/api/v1/dashboard/stats` | KPI metrics | VIEWER |
| GET | `/api/v1/dashboard/timeline` | Events timeline | VIEWER |
| GET | `/api/v1/dashboard/top-ips` | Top suspicious IPs | SOC_ANALYST |
| GET | `/api/v1/dashboard/top-users` | Top targeted users | SOC_ANALYST |
| GET | `/api/v1/dashboard/risk-evolution` | Risk score over time | SOC_ANALYST |

---

## WebSocket

| Endpoint | Description | Auth |
|----------|-------------|------|
| `WS /ws/alerts` | Real-time alert stream | JWT query param |
| `WS /ws/incidents` | Real-time incident updates | JWT query param |

**Message format** :
```json
{
  "type": "alert.created",
  "payload": { },
  "timestamp": "2026-08-18T01:00:00.000Z"
}
```

---

## Audit Logs

| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| GET | `/api/v1/audit-logs` | List audit logs | SOC_MANAGER |
| GET | `/api/v1/audit-logs/{id}` | Get audit log detail | SOC_MANAGER |

---

## Health & Metrics

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/health` | Service health check | Public |
| GET | `/health/kafka` | Kafka consumer health | Public |
| GET | `/metrics` | Prometheus metrics | Internal |

---

## Error Response Format

Toutes les erreurs suivent un format standard :

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid event_type. Must be one of: authentication, network, application, cloud",
    "details": [
      {
        "field": "event_type",
        "message": "Invalid value 'invalid_type'"
      }
    ],
    "request_id": "req-0195a3b2-abc123",
    "timestamp": "2026-08-18T01:00:00.000Z"
  }
}
```

| HTTP Code | Error Code | Description |
|-----------|-----------|-------------|
| 400 | BAD_REQUEST | Malformed request |
| 401 | UNAUTHORIZED | Missing or invalid token |
| 403 | FORBIDDEN | Insufficient permissions |
| 404 | NOT_FOUND | Resource not found |
| 422 | VALIDATION_ERROR | Pydantic validation failed |
| 429 | RATE_LIMITED | Too many requests |
| 500 | INTERNAL_ERROR | Server error |
| 503 | SERVICE_UNAVAILABLE | Downstream service unavailable |

---

## Rate Limits

| Endpoint Group | Limit | Window |
|---------------|-------|--------|
| Event ingestion | 1000 req/min | Per API key |
| AI endpoints | 30 req/min | Per user |
| Dashboard/Read | 300 req/min | Per user |
| Auth | 10 req/min | Per IP |

---

## Swagger UI

Disponible en dev sur : `http://localhost:8000/docs` (API Gateway)

Chaque microservice expose aussi sa propre doc :
- auth-service : `http://localhost:8001/docs`
- collector-service : `http://localhost:8002/docs`
- detection-service : `http://localhost:8003/docs`
- etc.
