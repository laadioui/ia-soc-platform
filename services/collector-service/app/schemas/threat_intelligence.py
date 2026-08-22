import uuid
from datetime import datetime

from pydantic import BaseModel


class ThreatIntelBase(BaseModel):
    indicator_type: str
    indicator_value: str
    threat_type: str | None = None
    confidence: float = 0.0
    severity: str = "medium"
    description: str | None = None
    source: str | None = None
    source_url: str | None = None


class ThreatIntelCreate(ThreatIntelBase):
    tags: list[str] | None = None
    related_campaign: str | None = None
    related_mitre: list[str] | None = None
    tlp: str | None = None


class ThreatIntelResponse(ThreatIntelBase):
    id: uuid.UUID
    tags: list | None = None
    related_campaign: str | None = None
    related_mitre: list | None = None
    is_active: bool
    tlp: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ThreatIntelListResponse(BaseModel):
    items: list[ThreatIntelResponse]
    total: int


class IOCResponse(BaseModel):
    id: uuid.UUID
    ioc_type: str
    ioc_value: str
    severity: str
    confidence: float
    description: str | None = None
    source: str | None = None
    threat_type: str | None = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class IOCCreate(BaseModel):
    ioc_type: str
    ioc_value: str
    severity: str = "medium"
    confidence: float = 0.0
    description: str | None = None
    source: str | None = None
    threat_type: str | None = None
    tags: list[str] | None = None
