import uuid
from datetime import datetime

from pydantic import BaseModel


class IncidentBase(BaseModel):
    title: str
    description: str | None = None
    severity: str
    source: str | None = None


class IncidentCreate(IncidentBase):
    risk_score: float = 0.0
    assigned_to: uuid.UUID | None = None
    tags: list[str] | None = None
    event_ids: list[uuid.UUID] | None = None


class IncidentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    severity: str | None = None
    status: str | None = None
    assigned_to: uuid.UUID | None = None
    risk_score: float | None = None
    tags: list[str] | None = None


class IncidentEventResponse(BaseModel):
    id: uuid.UUID
    event_id_str: str
    added_by: str
    notes: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class IncidentIOCResponse(BaseModel):
    id: uuid.UUID
    ioc_type: str
    ioc_value: str
    confidence: float | None = None
    source: str | None = None

    model_config = {"from_attributes": True}


class IncidentResponse(IncidentBase):
    id: uuid.UUID
    incident_id: str
    risk_score: float
    status: str
    assigned_to: uuid.UUID | None = None
    resolved_at: datetime | None = None
    contained_at: datetime | None = None
    ai_summary: str | None = None
    ai_confidence: float | None = None
    tags: list | None = None
    events: list[IncidentEventResponse] = []
    iocs: list[IncidentIOCResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IncidentListResponse(BaseModel):
    incidents: list[IncidentResponse]
    total: int
    page: int
    page_size: int


class IncidentTimeline(BaseModel):
    events: list[dict]
    alerts: list[dict]
    iocs: list[dict]
    mitre_techniques: list[dict]
    response_actions: list[dict]
    ai_analyses: list[dict]
