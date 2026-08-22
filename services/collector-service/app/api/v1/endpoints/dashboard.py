from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.alert import Alert
from app.models.event import SecurityEvent
from app.models.incident import Incident
from app.schemas.dashboard import (
    AlertsBySeverity,
    DashboardResponse,
    DashboardStats,
    EventsByHour,
    IncidentsByMachine,
    MITRETechniqueStats,
    TopAttackerIP,
    TopTargetedUser,
)

router = APIRouter()


@router.get("/", response_model=DashboardResponse)
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    now = datetime.now(timezone.utc)
    last_24h = now - timedelta(hours=24)

    total_events = (await db.execute(select(func.count(SecurityEvent.id)))).scalar() or 0
    events_24h = (await db.execute(
        select(func.count(SecurityEvent.id)).where(SecurityEvent.timestamp >= last_24h)
    )).scalar() or 0

    critical_alerts = (await db.execute(
        select(func.count(Alert.id)).where(
            Alert.severity == "critical", Alert.status.in_(["new", "acknowledged"])
        )
    )).scalar() or 0

    open_incidents = (await db.execute(
        select(func.count(Incident.id)).where(
            Incident.status.in_(["new", "investigating"])
        )
    )).scalar() or 0

    resolved_incidents = (await db.execute(
        select(func.count(Incident.id)).where(Incident.status == "resolved")
    )).scalar() or 0

    high_risk_ips_result = await db.execute(
        select(SecurityEvent.source_ip, func.count(SecurityEvent.id).label("cnt"))
        .where(SecurityEvent.source_ip.isnot(None))
        .group_by(SecurityEvent.source_ip)
        .having(func.count(SecurityEvent.id) > 10)
        .order_by(func.count(SecurityEvent.id).desc())
        .limit(10)
    )
    high_risk_ips = len(high_risk_ips_result.all())

    events_by_hour = []
    for i in range(24):
        hour_start = last_24h + timedelta(hours=i)
        hour_end = hour_start + timedelta(hours=1)
        count = (await db.execute(
            select(func.count(SecurityEvent.id)).where(
                SecurityEvent.timestamp >= hour_start,
                SecurityEvent.timestamp < hour_end,
            )
        )).scalar() or 0
        events_by_hour.append(EventsByHour(hour=hour_start.strftime("%H:00"), count=count))

    alerts_by_severity = []
    for sev in ["critical", "high", "medium", "low", "info"]:
        count = (await db.execute(
            select(func.count(Alert.id)).where(Alert.severity == sev)
        )).scalar() or 0
        alerts_by_severity.append(AlertsBySeverity(severity=sev, count=count))

    top_ips_result = await db.execute(
        select(SecurityEvent.source_ip, func.count(SecurityEvent.id).label("cnt"))
        .where(SecurityEvent.source_ip.isnot(None))
        .group_by(SecurityEvent.source_ip)
        .order_by(func.count(SecurityEvent.id).desc())
        .limit(5)
    )
    top_attacker_ips = [
        TopAttackerIP(ip=row[0], count=row[1], severity="high") for row in top_ips_result.all()
    ]

    top_users_result = await db.execute(
        select(SecurityEvent.user_name, func.count(SecurityEvent.id).label("cnt"))
        .where(SecurityEvent.user_name.isnot(None))
        .group_by(SecurityEvent.user_name)
        .order_by(func.count(SecurityEvent.id).desc())
        .limit(5)
    )
    top_targeted_users = [
        TopTargetedUser(username=row[0], count=row[1]) for row in top_users_result.all()
    ]

    return DashboardResponse(
        stats=DashboardStats(
            total_events=total_events,
            events_24h=events_24h,
            critical_alerts=critical_alerts,
            open_incidents=open_incidents,
            resolved_incidents=resolved_incidents,
            high_risk_ips=high_risk_ips,
            active_threats=critical_alerts,
            detection_rate=0.0,
            false_positive_rate=0.0,
        ),
        events_by_hour=events_by_hour,
        alerts_by_severity=alerts_by_severity,
        top_attacker_ips=top_attacker_ips,
        top_targeted_users=top_targeted_users,
        incidents_by_machine=[],
        mitre_techniques=[],
    )
