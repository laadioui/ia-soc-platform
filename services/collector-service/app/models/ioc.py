import uuid

from sqlalchemy import Float, Index, String, Text, Uuid, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class IOC(TimestampMixin, Base):
    __tablename__ = "iocs"
    __table_args__ = (
        Index("idx_iocs_type", "ioc_type"),
        Index("idx_iocs_value", "ioc_value"),
        Index("idx_iocs_severity", "severity"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    ioc_type: Mapped[str] = mapped_column(String(50), nullable=False)
    ioc_value: Mapped[str] = mapped_column(String(500), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="medium")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    description: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(String(255))
    tags: Mapped[list | None] = mapped_column(JSON)
    first_seen: Mapped[str | None] = mapped_column(String(50))
    last_seen: Mapped[str | None] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(default=True)
    threat_type: Mapped[str | None] = mapped_column(String(100))
    related_campaign: Mapped[str | None] = mapped_column(String(255))
