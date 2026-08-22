import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.incident import Incident
from app.schemas.incident import (
    IncidentCreate,
    IncidentListResponse,
    IncidentResponse,
    IncidentTimeline,
    IncidentUpdate,
)

router = APIRouter()

incident_counter = 0


def generate_incident_id() -> str:
    global incident_counter
    incident_counter += 1
    return f"INC-2026-{incident_counter:04d}"


@router.get("/", response_model=IncidentListResponse)
async def list_incidents(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    status_filter: str | None = Query(None, alias="status"),
    severity: str | None = None,
    assigned_to: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Incident).options(
        selectinload(Incident.events),
        selectinload(Incident.iocs),
    )
    count_query = select(func.count(Incident.id))

    if status_filter:
        query = query.where(Incident.status == status_filter)
        count_query = count_query.where(Incident.status == status_filter)
    if severity:
        query = query.where(Incident.severity == severity)
        count_query = count_query.where(Incident.severity == severity)
    if assigned_to:
        query = query.where(Incident.assigned_to == assigned_to)
        count_query = count_query.where(Incident.assigned_to == assigned_to)

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * page_size
    query = query.order_by(Incident.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    incidents = result.scalars().unique().all()

    return IncidentListResponse(incidents=incidents, total=total, page=page, page_size=page_size)


@router.post("/", response_model=IncidentResponse, status_code=201)
async def create_incident(data: IncidentCreate, db: AsyncSession = Depends(get_db)):
    incident = Incident(
        incident_id=generate_incident_id(),
        title=data.title,
        description=data.description,
        severity=data.severity,
        risk_score=data.risk_score,
        source=data.source,
        assigned_to=data.assigned_to,
        tags=data.tags,
    )
    db.add(incident)
    await db.flush()
    await db.refresh(incident)
    return incident


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Incident)
        .options(selectinload(Incident.events), selectinload(Incident.iocs))
        .where(Incident.id == incident_id)
    )
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.put("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: uuid.UUID,
    data: IncidentUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Incident)
        .options(selectinload(Incident.events), selectinload(Incident.iocs))
        .where(Incident.id == incident_id)
    )
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(incident, field, value)

    await db.flush()
    await db.refresh(incident)
    return incident


@router.get("/{incident_id}/timeline", response_model=IncidentTimeline)
async def get_incident_timeline(incident_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Incident)
        .options(
            selectinload(Incident.events),
            selectinload(Incident.iocs),
            selectinload(Incident.mitre_mappings),
            selectinload(Incident.response_actions),
            selectinload(Incident.ai_analyses),
        )
        .where(Incident.id == incident_id)
    )
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    return IncidentTimeline(
        events=[
            {
                "event_id": e.event_id_str,
                "added_by": e.added_by,
                "notes": e.notes,
                "timestamp": e.created_at.isoformat(),
            }
            for e in incident.events
        ],
        alerts=[],
        iocs=[{"type": i.ioc_type, "value": i.ioc_value, "confidence": i.confidence} for i in incident.iocs],
        mitre_techniques=[
            {"technique_id": m.technique_id, "confidence": m.confidence} for m in incident.mitre_mappings
        ],
        response_actions=[
            {"type": a.action_type, "target": a.target, "status": a.status, "is_simulated": a.is_simulated}
            for a in incident.response_actions
        ],
        ai_analyses=[
            {"type": a.analysis_type, "response": a.response[:200], "confidence": a.confidence}
            for a in incident.ai_analyses
        ],
    )
