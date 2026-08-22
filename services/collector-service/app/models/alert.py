import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, String, Text, Uuid, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Alert(TimestampMixin, Base):
    __tablename__ = "alerts"
    __table_args__ = (
        Index("idx_alerts_status", "status"),
        Index("idx_alerts_severity", "severity"),
        Index("idx_alerts_created", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    alert_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="new", nullable=False)
    risk_score: Mapped[float | None] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    rule_id: Mapped[str | None] = mapped_column(String(100))
    rule_name: Mapped[str | None] = mapped_column(String(255))
    event_count: Mapped[int] = mapped_column(default=1)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("users.id"))
    metadata_json: Mapped[dict | None] = mapped_column(JSON)
    related_events: Mapped[list | None] = mapped_column(JSON)

    assignee = relationship("User", foreign_keys=[assigned_to])
