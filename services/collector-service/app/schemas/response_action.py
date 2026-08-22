import uuid
from datetime import datetime

from pydantic import BaseModel


class ResponseActionCreate(BaseModel):
    action_type: str
    target: str
    parameters: dict | None = None


class ResponseActionResponse(BaseModel):
    id: uuid.UUID
    incident_id: uuid.UUID
    action_type: str
    target: str
    status: str
    executed_by: str | None = None
    executed_at: datetime | None = None
    result: str | None = None
    is_simulated: bool
    parameters: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class BlockIPRequest(BaseModel):
    ip_address: str
    incident_id: uuid.UUID | None = None
    reason: str | None = None


class DisableUserRequest(BaseModel):
    username: str
    incident_id: uuid.UUID | None = None
    reason: str | None = None


class KillSessionRequest(BaseModel):
    session_id: str
    incident_id: uuid.UUID | None = None


class ResetPasswordRequest(BaseModel):
    username: str
    incident_id: uuid.UUID | None = None
