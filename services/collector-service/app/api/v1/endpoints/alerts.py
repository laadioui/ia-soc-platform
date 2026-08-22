import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.alert import Alert
from app.schemas.alert import AlertListResponse, AlertResponse, AlertUpdate

router = APIRouter()


@router.get("/", response_model=AlertListResponse)
async def list_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    status_filter: str | None = Query(None, alias="status"),
    severity: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Alert)
    count_query = select(func.count(Alert.id))

    if status_filter:
        query = query.where(Alert.status == status_filter)
        count_query = count_query.where(Alert.status == status_filter)
    if severity:
        query = query.where(Alert.severity == severity)
        count_query = count_query.where(Alert.severity == severity)

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * page_size
    query = query.order_by(Alert.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    alerts = result.scalars().all()

    return AlertListResponse(alerts=alerts, total=total, page=page, page_size=page_size)


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.put("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: uuid.UUID,
    update_data: AlertUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(alert, field, value)

    await db.flush()
    await db.refresh(alert)
    return alert
