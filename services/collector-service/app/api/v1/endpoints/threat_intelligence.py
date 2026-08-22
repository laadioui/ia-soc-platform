import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.ioc import IOC
from app.models.threat_intelligence import ThreatIntelligence
from app.schemas.threat_intelligence import (
    IOCCreate,
    IOCResponse,
    ThreatIntelCreate,
    ThreatIntelListResponse,
    ThreatIntelResponse,
)

router = APIRouter()


@router.get("/", response_model=ThreatIntelListResponse)
async def list_threat_intelligence(
    skip: int = 0,
    limit: int = 50,
    indicator_type: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(ThreatIntelligence)
    count_query = select(func.count(ThreatIntelligence.id))

    if indicator_type:
        query = query.where(ThreatIntelligence.indicator_type == indicator_type)
        count_query = count_query.where(ThreatIntelligence.indicator_type == indicator_type)

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.order_by(ThreatIntelligence.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()

    return ThreatIntelListResponse(items=items, total=total)


@router.post("/", response_model=ThreatIntelResponse, status_code=201)
async def create_threat_intel(data: ThreatIntelCreate, db: AsyncSession = Depends(get_db)):
    ti = ThreatIntelligence(**data.model_dump())
    db.add(ti)
    await db.flush()
    await db.refresh(ti)
    return ti


@router.get("/lookup/{indicator_value}")
async def lookup_indicator(indicator_value: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ThreatIntelligence).where(
            ThreatIntelligence.indicator_value == indicator_value,
            ThreatIntelligence.is_active == True,
        )
    )
    ti = result.scalar_one_or_none()
    if not ti:
        return {"found": False, "indicator": indicator_value}

    return {
        "found": True,
        "indicator": indicator_value,
        "threat_type": ti.threat_type,
        "confidence": ti.confidence,
        "severity": ti.severity,
        "source": ti.source,
        "related_campaign": ti.related_campaign,
        "tags": ti.tags,
    }


@router.get("/iocs", response_model=list[IOCResponse])
async def list_iocs(
    skip: int = 0,
    limit: int = 50,
    ioc_type: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(IOC)
    if ioc_type:
        query = query.where(IOC.ioc_type == ioc_type)
    query = query.order_by(IOC.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/iocs", response_model=IOCResponse, status_code=201)
async def create_ioc(data: IOCCreate, db: AsyncSession = Depends(get_db)):
    ioc = IOC(**data.model_dump())
    db.add(ioc)
    await db.flush()
    await db.refresh(ioc)
    return ioc
