import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    model_id = Column(UUID(as_uuid=True), ForeignKey("ai_models.id"), nullable=False)

    category = Column(String, nullable=False)
    prompt_hash = Column(String, nullable=False)
    recommendation_text = Column(Text, nullable=False)
    diff_ref = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    prev_hash = Column(String, nullable=True)
    row_hash = Column(String, nullable=False)

    user = relationship("User", back_populates="decisions")
    model = relationship("AIModel", back_populates="decisions")
