import uuid
from datetime import datetime

from pydantic import BaseModel


class DetectionRuleBase(BaseModel):
    name: str
    description: str | None = None
    rule_type: str
    severity: str
    category: str
    condition: dict
    mitre_technique: str | None = None
    mitre_tactic: str | None = None


class DetectionRuleCreate(DetectionRuleBase):
    rule_id: str
    false_positive_check: str | None = None
    is_active: bool = True
    author: str | None = None
    tags: list[str] | None = None
    time_window_seconds: int | None = None
    threshold: int | None = None


class DetectionRuleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    severity: str | None = None
    category: str | None = None
    condition: dict | None = None
    is_active: bool | None = None
    mitre_technique: str | None = None
    mitre_tactic: str | None = None
    tags: list[str] | None = None


class DetectionRuleResponse(DetectionRuleBase):
    id: uuid.UUID
    rule_id: str
    false_positive_check: str | None = None
    is_active: bool
    version: int
    author: str | None = None
    tags: list | None = None
    time_window_seconds: int | None = None
    threshold: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
