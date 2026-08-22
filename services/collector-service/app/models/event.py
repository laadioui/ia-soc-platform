import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class SecurityEvent(TimestampMixin, Base):
    __tablename__ = "events"
    __table_args__ = (
        Index("idx_events_timestamp", "timestamp"),
        Index("idx_events_source", "source"),
        Index("idx_events_category", "category"),
        Index("idx_events_severity", "severity"),
        Index("idx_events_source_ip", "source_ip"),
        Index("idx_events_user", "user_name"),
        Index("idx_events_category_timestamp", "category", "timestamp"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    event_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    user_name: Mapped[str | None] = mapped_column(String(255), index=True)
    source_ip: Mapped[str | None] = mapped_column(String(45), index=True)
    destination_ip: Mapped[str | None] = mapped_column(String(45))
    destination_port: Mapped[int | None] = mapped_column()
    hostname: Mapped[str | None] = mapped_column(String(255))
    application: Mapped[str | None] = mapped_column(String(255))
    severity: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    raw_event: Mapped[dict | None] = mapped_column(JSON)
    normalized_event: Mapped[dict | None] = mapped_column(JSON)
    tags: Mapped[list | None] = mapped_column(JSON)
    risk_score: Mapped[float | None] = mapped_column(Float)
    is_alert: Mapped[bool] = mapped_column(default=False)
    processed: Mapped[bool] = mapped_column(default=False)
