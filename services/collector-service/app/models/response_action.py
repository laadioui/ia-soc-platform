import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class ResponseAction(TimestampMixin, Base):
    __tablename__ = "response_actions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    incident_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("incidents.id"), nullable=False)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    executed_by: Mapped[str | None] = mapped_column(String(255))
    executed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    result: Mapped[str | None] = mapped_column(Text)
    is_simulated: Mapped[bool] = mapped_column(default=True)
    parameters: Mapped[dict | None] = mapped_column(JSON)

    incident = relationship("Incident", back_populates="response_actions")
