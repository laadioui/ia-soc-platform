from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_events: int
    events_24h: int
    critical_alerts: int
    open_incidents: int
    resolved_incidents: int
    high_risk_ips: int
    active_threats: int
    detection_rate: float
    false_positive_rate: float


class EventsByHour(BaseModel):
    hour: str
    count: int


class AlertsBySeverity(BaseModel):
    severity: str
    count: int


class TopAttackerIP(BaseModel):
    ip: str
    count: int
    severity: str


class TopTargetedUser(BaseModel):
    username: str
    count: int


class IncidentsByMachine(BaseModel):
    hostname: str
    count: int


class MITRETechniqueStats(BaseModel):
    technique_id: str
    name: str
    count: int


class DashboardResponse(BaseModel):
    stats: DashboardStats
    events_by_hour: list[EventsByHour]
    alerts_by_severity: list[AlertsBySeverity]
    top_attacker_ips: list[TopAttackerIP]
    top_targeted_users: list[TopTargetedUser]
    incidents_by_machine: list[IncidentsByMachine]
    mitre_techniques: list[MITRETechniqueStats]
