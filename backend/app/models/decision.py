import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.session import Base


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    model_id = Column(UUID(as_uuid=True), ForeignKey("ai_models.id"), nullable=False)

    category = Column(String, nullable=False)
    title = Column(String(200), nullable=True)
    diff_content = Column(Text, nullable=True)
    affected_files = Column(JSONB, nullable=False, default=list)
    status = Column(String(32), nullable=False, default="captured")
    hash_version = Column(Integer, nullable=False, default=3)
    prompt_hash = Column(String, nullable=False)
    recommendation_text = Column(Text, nullable=False)
    diff_ref = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    prev_hash = Column(String, nullable=True)
    row_hash = Column(String, nullable=False)

    user = relationship("User", back_populates="decisions")
    model = relationship("AIModel", back_populates="decisions")
