import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DecisionCreate(BaseModel):
    org_id: Optional[uuid.UUID] = None
    user_id: uuid.UUID
    model_id: uuid.UUID
    category: str
    prompt_hash: str
    recommendation_text: str
    diff_ref: Optional[str] = None


class DecisionResponse(BaseModel):
    id: uuid.UUID
    org_id: Optional[uuid.UUID]
    user_id: uuid.UUID
    model_id: uuid.UUID
    category: str
    prompt_hash: str
    recommendation_text: str
    diff_ref: Optional[str]
    created_at: datetime
    prev_hash: Optional[str]
    row_hash: str

    class Config:
        from_attributes = True
