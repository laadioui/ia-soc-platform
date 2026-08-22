import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.detection_rule import DetectionRule
from app.schemas.detection_rule import DetectionRuleCreate, DetectionRuleResponse, DetectionRuleUpdate

router = APIRouter()


@router.get("/", response_model=list[DetectionRuleResponse])
async def list_rules(
    skip: int = 0,
    limit: int = 50,
    rule_type: str | None = None,
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(DetectionRule)
    if rule_type:
        query = query.where(DetectionRule.rule_type == rule_type)
    if is_active is not None:
        query = query.where(DetectionRule.is_active == is_active)
    query = query.order_by(DetectionRule.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=DetectionRuleResponse, status_code=201)
async def create_rule(data: DetectionRuleCreate, db: AsyncSession = Depends(get_db)):
    rule = DetectionRule(**data.model_dump())
    db.add(rule)
    await db.flush()
    await db.refresh(rule)
    return rule


@router.get("/{rule_id}", response_model=DetectionRuleResponse)
async def get_rule(rule_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DetectionRule).where(DetectionRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.put("/{rule_id}", response_model=DetectionRuleResponse)
async def update_rule(
    rule_id: uuid.UUID,
    data: DetectionRuleUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(DetectionRule).where(DetectionRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(rule, field, value)

    rule.version += 1
    await db.flush()
    await db.refresh(rule)
    return rule
