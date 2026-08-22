import uuid

from sqlalchemy import JSON, Float, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class AIAnalysis(TimestampMixin, Base):
    __tablename__ = "ai_analyses"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    incident_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("incidents.id"))
    event_id: Mapped[uuid.UUID | None] = mapped_column(Uuid)
    analysis_type: Mapped[str] = mapped_column(String(50), nullable=False)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[str] = mapped_column(Text, nullable=False)
    model_used: Mapped[str | None] = mapped_column(String(100))
    confidence: Mapped[float | None] = mapped_column(Float)
    context_used: Mapped[list | None] = mapped_column(JSON)
    tokens_used: Mapped[int | None] = mapped_column()
    processing_time_ms: Mapped[float | None] = mapped_column(Float)
    feedback: Mapped[str | None] = mapped_column(String(20))

    incident = relationship("Incident", back_populates="ai_analyses")
