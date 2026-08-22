import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.mitre import MITRETechnique
from app.schemas.mitre import MITRETechniqueResponse

router = APIRouter()


@router.get("/", response_model=list[MITRETechniqueResponse])
async def list_mitre_techniques(
    tactic: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(MITRETechnique)
    if tactic:
        query = query.where(MITRETechnique.tactic == tactic)
    query = query.order_by(MITRETechnique.technique_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{technique_id}", response_model=MITRETechniqueResponse)
async def get_mitre_technique(technique_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(MITRETechnique).where(MITRETechnique.technique_id == technique_id)
    )
    technique = result.scalar_one_or_none()
    if not technique:
        raise HTTPException(status_code=404, detail="MITRE technique not found")
    return technique


@router.get("/tactics/list")
async def list_tactics(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(MITRETechnique.tactic).distinct().order_by(MITRETechnique.tactic)
    )
    tactics = [row[0] for row in result.all()]
    return {"tactics": tactics}
