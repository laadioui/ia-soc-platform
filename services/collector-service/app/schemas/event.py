import uuid
from datetime import datetime

from pydantic import BaseModel


class EventBase(BaseModel):
    source: str
    source_type: str
    category: str
    action: str
    severity: str = "info"
    user_name: str | None = None
    source_ip: str | None = None
    destination_ip: str | None = None
    destination_port: int | None = None
    hostname: str | None = None
    application: str | None = None


class EventCreate(EventBase):
    timestamp: datetime | None = None
    raw_event: dict | None = None
    tags: list[str] | None = None


class EventBulkCreate(BaseModel):
    events: list[EventCreate]


class EventResponse(EventBase):
    id: uuid.UUID
    event_id: str
    timestamp: datetime
    risk_score: float | None = None
    is_alert: bool = False
    processed: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class EventListResponse(BaseModel):
    events: list[EventResponse]
    total: int
    page: int
    page_size: int


class EventFilter(BaseModel):
    source: str | None = None
    category: str | None = None
    severity: str | None = None
    source_ip: str | None = None
    user_name: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    search: str | None = None
