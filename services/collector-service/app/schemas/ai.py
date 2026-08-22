from pydantic import BaseModel


class AIAnalyzeRequest(BaseModel):
    query: str
    incident_id: str | None = None
    event_ids: list[str] | None = None
    context: dict | None = None


class AIAnalyzeResponse(BaseModel):
    response: str
    confidence: float | None = None
    model_used: str | None = None
    tokens_used: int | None = None
    processing_time_ms: float | None = None
    context_sources: list[str] = []


class AISummarizeRequest(BaseModel):
    incident_id: str
    include_events: bool = True
    include_iocs: bool = True
    include_mitre: bool = True


class AISummarizeResponse(BaseModel):
    summary: str
    key_findings: list[str]
    risk_assessment: str
    recommended_actions: list[str]
    mitre_techniques: list[str]
    confidence: float


class AIIncidentAnalysis(BaseModel):
    overview: str
    attack_chain: list[str]
    affected_assets: list[str]
    threat_level: str
    confidence: float
    recommendations: list[str]
