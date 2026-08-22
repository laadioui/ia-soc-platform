import uuid
from datetime import datetime

from pydantic import BaseModel


class AlertBase(BaseModel):
    title: str
    description: str | None = None
    severity: str
    source: str
    rule_id: str | None = None
    rule_name: str | None = None


class AlertCreate(AlertBase):
    risk_score: float | None = None
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    event_count: int = 1
    related_events: list[dict] | None = None
    metadata_json: dict | None = None


class AlertUpdate(BaseModel):
    status: str | None = None
    severity: str | None = None
    assigned_to: uuid.UUID | None = None
    notes: str | None = None


class AlertResponse(AlertBase):
    id: uuid.UUID
    alert_id: str
    status: str
    risk_score: float | None = None
    event_count: int
    first_seen: datetime
    last_seen: datetime
    acknowledged_at: datetime | None = None
    resolved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AlertListResponse(BaseModel):
    alerts: list[AlertResponse]
    total: int
    page: int
    page_size: int
