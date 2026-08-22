import uuid

from sqlalchemy import JSON, Float, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class MITRETechnique(TimestampMixin, Base):
    __tablename__ = "mitre_techniques"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    technique_id: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tactic: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    detection: Mapped[str | None] = mapped_column(Text)
    platforms: Mapped[list | None] = mapped_column(JSON)
    data_sources: Mapped[list | None] = mapped_column(JSON)
    sub_techniques: Mapped[list | None] = mapped_column(JSON)


class IncidentMITREMapping(TimestampMixin, Base):
    __tablename__ = "incident_mitre_mappings"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    incident_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("incidents.id"), nullable=False)
    technique_id: Mapped[str] = mapped_column(String(20), ForeignKey("mitre_techniques.technique_id"), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    context: Mapped[str | None] = mapped_column(Text)

    incident = relationship("Incident", back_populates="mitre_mappings")
    technique = relationship("MITRETechnique")
