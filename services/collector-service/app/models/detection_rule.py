import uuid

from sqlalchemy import JSON, Boolean, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class DetectionRule(TimestampMixin, Base):
    __tablename__ = "detection_rules"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    rule_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    condition: Mapped[dict] = mapped_column(JSON, nullable=False)
    mitre_technique: Mapped[str | None] = mapped_column(String(20))
    mitre_tactic: Mapped[str | None] = mapped_column(String(100))
    false_positive_check: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    author: Mapped[str | None] = mapped_column(String(255))
    tags: Mapped[list | None] = mapped_column(JSON)
    time_window_seconds: Mapped[int | None] = mapped_column(Integer)
    threshold: Mapped[int | None] = mapped_column(Integer)
