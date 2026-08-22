import uuid

from sqlalchemy import Boolean, String, Text, Uuid, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class Asset(TimestampMixin, Base):
    __tablename__ = "assets"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    asset_type: Mapped[str] = mapped_column(String(50), nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(45), index=True)
    hostname: Mapped[str | None] = mapped_column(String(255))
    operating_system: Mapped[str | None] = mapped_column(String(100))
    owner: Mapped[str | None] = mapped_column(String(255))
    environment: Mapped[str | None] = mapped_column(String(50))
    criticality: Mapped[str] = mapped_column(String(20), default="medium")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON)
    description: Mapped[str | None] = mapped_column(Text)
