import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.event import SecurityEvent
from app.schemas.event import EventBulkCreate, EventCreate, EventListResponse, EventResponse

router = APIRouter()

SOURCE_TYPE_MAP = {
    "linux": "server",
    "windows": "server",
    "nginx": "application",
    "docker": "container",
    "kubernetes": "orchestrator",
    "aws-cloudtrail": "cloud",
    "web-application": "application",
}


def generate_event_id() -> str:
    return f"evt-{uuid.uuid4().hex[:12]}"


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def ingest_event(event_data: EventCreate, db: AsyncSession = Depends(get_db)):
    event = SecurityEvent(
        event_id=generate_event_id(),
        timestamp=event_data.timestamp or datetime.now(timezone.utc),
        source=event_data.source,
        source_type=SOURCE_TYPE_MAP.get(event_data.source_type, event_data.source_type),
        category=event_data.category,
        action=event_data.action,
        severity=event_data.severity,
        user_name=event_data.user_name,
        source_ip=event_data.source_ip,
        destination_ip=event_data.destination_ip,
        destination_port=event_data.destination_port,
        hostname=event_data.hostname,
        application=event_data.application,
        raw_event=event_data.raw_event,
        tags=event_data.tags,
    )
    db.add(event)
    await db.flush()
    await db.refresh(event)
    return event


@router.post("/bulk", response_model=dict, status_code=status.HTTP_201_CREATED)
async def ingest_events_bulk(bulk_data: EventBulkCreate, db: AsyncSession = Depends(get_db)):
    events = []
    for event_data in bulk_data.events:
        event = SecurityEvent(
            event_id=generate_event_id(),
            timestamp=event_data.timestamp or datetime.now(timezone.utc),
            source=event_data.source,
            source_type=SOURCE_TYPE_MAP.get(event_data.source_type, event_data.source_type),
            category=event_data.category,
            action=event_data.action,
            severity=event_data.severity,
            user_name=event_data.user_name,
            source_ip=event_data.source_ip,
            destination_ip=event_data.destination_ip,
            destination_port=event_data.destination_port,
            hostname=event_data.hostname,
            application=event_data.application,
            raw_event=event_data.raw_event,
            tags=event_data.tags,
        )
        db.add(event)
        events.append(event)

    await db.flush()
    return {"ingested": len(events), "status": "success"}


@router.get("/", response_model=EventListResponse)
async def list_events(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    source: str | None = None,
    category: str | None = None,
    severity: str | None = None,
    source_ip: str | None = None,
    user_name: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(SecurityEvent)
    count_query = select(func.count(SecurityEvent.id))

    if source:
        query = query.where(SecurityEvent.source == source)
        count_query = count_query.where(SecurityEvent.source == source)
    if category:
        query = query.where(SecurityEvent.category == category)
        count_query = count_query.where(SecurityEvent.category == category)
    if severity:
        query = query.where(SecurityEvent.severity == severity)
        count_query = count_query.where(SecurityEvent.severity == severity)
    if source_ip:
        query = query.where(SecurityEvent.source_ip == source_ip)
        count_query = count_query.where(SecurityEvent.source_ip == source_ip)
    if user_name:
        query = query.where(SecurityEvent.user_name == user_name)
        count_query = count_query.where(SecurityEvent.user_name == user_name)
    if start_date:
        query = query.where(SecurityEvent.timestamp >= start_date)
        count_query = count_query.where(SecurityEvent.timestamp >= start_date)
    if end_date:
        query = query.where(SecurityEvent.timestamp <= end_date)
        count_query = count_query.where(SecurityEvent.timestamp <= end_date)

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * page_size
    query = query.order_by(SecurityEvent.timestamp.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    events = result.scalars().all()

    return EventListResponse(events=events, total=total, page=page, page_size=page_size)


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SecurityEvent).where(SecurityEvent.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event
