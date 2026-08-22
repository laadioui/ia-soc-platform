from fastapi import APIRouter

from app.api.v1.endpoints import (
    ai,
    alerts,
    auth,
    dashboard,
    detection_rules,
    events,
    incidents,
    mitre,
    response,
    threat_intelligence,
    users,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(events.router, prefix="/events", tags=["Events"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["Incidents"])
api_router.include_router(threat_intelligence.router, prefix="/threat-intelligence", tags=["Threat Intelligence"])
api_router.include_router(mitre.router, prefix="/mitre", tags=["MITRE ATT&CK"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI Engine"])
api_router.include_router(response.router, prefix="/response", tags=["Response / SOAR"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(detection_rules.router, prefix="/detection-rules", tags=["Detection Rules"])
