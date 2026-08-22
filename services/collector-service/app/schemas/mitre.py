import uuid

from pydantic import BaseModel


class MITRETechniqueResponse(BaseModel):
    id: uuid.UUID
    technique_id: str
    name: str
    tactic: str
    description: str | None = None
    detection: str | None = None
    platforms: list | None = None
    sub_techniques: list | None = None

    model_config = {"from_attributes": True}


class MITREMappingCreate(BaseModel):
    technique_id: str
    confidence: float = 0.0
    context: str | None = None


class MITREMappingResponse(BaseModel):
    id: uuid.UUID
    technique_id: str
    confidence: float
    context: str | None = None
    technique: MITRETechniqueResponse | None = None

    model_config = {"from_attributes": True}
