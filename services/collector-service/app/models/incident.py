import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.ai_analysis import AIAnalysis
    from app.models.mitre import IncidentMITREMapping
    from app.models.response_action import ResponseAction


class Incident(TimestampMixin, Base):
    __tablename__ = "incidents"
    __table_args__ = (
        Index("idx_incidents_status", "status"),
        Index("idx_incidents_severity", "severity"),
        Index("idx_incidents_created", "created_at"),
        Index("idx_incidents_assigned", "assigned_to"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    incident_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(30), default="new", nullable=False)
    source: Mapped[str | None] = mapped_column(String(255))
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("users.id"))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    contained_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ai_summary: Mapped[str | None] = mapped_column(Text)
    ai_confidence: Mapped[float | None] = mapped_column(Float)
    tags: Mapped[list | None] = mapped_column(JSON)
    metadata_json: Mapped[dict | None] = mapped_column(JSON)

    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_incidents", lazy="selectin")
    events: Mapped[list["IncidentEvent"]] = relationship(
        back_populates="incident", cascade="all, delete-orphan", lazy="selectin"
    )
    iocs: Mapped[list["IncidentIOC"]] = relationship(
        back_populates="incident", cascade="all, delete-orphan", lazy="selectin"
    )
    mitre_mappings: Mapped[list["IncidentMITREMapping"]] = relationship(back_populates="incident", lazy="selectin")
    ai_analyses: Mapped[list["AIAnalysis"]] = relationship("AIAnalysis", back_populates="incident", lazy="selectin")
    response_actions: Mapped[list["ResponseAction"]] = relationship(
        "ResponseAction", back_populates="incident", lazy="selectin"
    )


class IncidentEvent(TimestampMixin, Base):
    __tablename__ = "incident_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    incident_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("incidents.id"), nullable=False)
    event_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    event_id_str: Mapped[str] = mapped_column(String(255), nullable=False)
    added_by: Mapped[str] = mapped_column(String(100), default="system")
    notes: Mapped[str | None] = mapped_column(Text)

    incident: Mapped["Incident"] = relationship(back_populates="events", lazy="selectin")


class IncidentIOC(TimestampMixin, Base):
    __tablename__ = "incident_iocs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    incident_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("incidents.id"), nullable=False)
    ioc_type: Mapped[str] = mapped_column(String(50), nullable=False)
    ioc_value: Mapped[str] = mapped_column(String(500), nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float)
    source: Mapped[str | None] = mapped_column(String(255))

    incident: Mapped["Incident"] = relationship(back_populates="iocs", lazy="selectin")
