import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.response_action import ResponseAction
from app.schemas.response_action import (
    BlockIPRequest,
    DisableUserRequest,
    KillSessionRequest,
    ResetPasswordRequest,
    ResponseActionResponse,
)

router = APIRouter()


async def _create_response_action(
    db: AsyncSession,
    incident_id: uuid.UUID | None,
    action_type: str,
    target: str,
    parameters: dict | None = None,
) -> ResponseAction:
    action = ResponseAction(
        incident_id=incident_id or uuid.uuid4(),
        action_type=action_type,
        target=target,
        status="completed",
        executed_by="system",
        executed_at=datetime.now(UTC),
        result=f"Simulated: {action_type} applied to {target}",
        is_simulated=True,
        parameters=parameters,
    )
    db.add(action)
    await db.flush()
    await db.refresh(action)
    return action


@router.post("/block-ip", response_model=ResponseActionResponse)
async def block_ip(data: BlockIPRequest, db: AsyncSession = Depends(get_db)):
    action = await _create_response_action(db, data.incident_id, "block_ip", data.ip_address, {"reason": data.reason})
    return action


@router.post("/disable-user", response_model=ResponseActionResponse)
async def disable_user(data: DisableUserRequest, db: AsyncSession = Depends(get_db)):
    action = await _create_response_action(db, data.incident_id, "disable_user", data.username, {"reason": data.reason})
    return action


@router.post("/kill-session", response_model=ResponseActionResponse)
async def kill_session(data: KillSessionRequest, db: AsyncSession = Depends(get_db)):
    action = await _create_response_action(db, data.incident_id, "kill_session", data.session_id)
    return action


@router.post("/isolate-host", response_model=ResponseActionResponse)
async def isolate_host(
    host: str,
    incident_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    action = await _create_response_action(db, incident_id, "isolate_host", host)
    return action


@router.post("/reset-password", response_model=ResponseActionResponse)
async def reset_password(data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    action = await _create_response_action(db, data.incident_id, "reset_password", data.username)
    return action


@router.post("/create-firewall-rule", response_model=ResponseActionResponse)
async def create_firewall_rule(
    rule_description: str,
    incident_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    action = await _create_response_action(db, incident_id, "create_firewall_rule", rule_description)
    return action
