import uuid

from sqlalchemy import JSON, Float, Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class ThreatIntelligence(TimestampMixin, Base):
    __tablename__ = "threat_intelligence"
    __table_args__ = (
        Index("idx_ti_type", "indicator_type"),
        Index("idx_ti_value", "indicator_value"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    indicator_type: Mapped[str] = mapped_column(String(50), nullable=False)
    indicator_value: Mapped[str] = mapped_column(String(500), nullable=False)
    threat_type: Mapped[str | None] = mapped_column(String(100))
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    severity: Mapped[str] = mapped_column(String(20), default="medium")
    description: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(String(255))
    source_url: Mapped[str | None] = mapped_column(String(1000))
    tags: Mapped[list | None] = mapped_column(JSON)
    related_campaign: Mapped[str | None] = mapped_column(String(255))
    related_mitre: Mapped[list | None] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(default=True)
    tlp: Mapped[str | None] = mapped_column(String(20))
