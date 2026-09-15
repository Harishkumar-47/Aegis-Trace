import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.decision import Decision
from app.schemas.decision import DecisionCreate, DecisionResponse
from app.services.ledger import compute_row_hash, get_latest_row_hash

router = APIRouter(prefix="/api/decisions", tags=["decisions"])


@router.post("", response_model=DecisionResponse)
def create_decision(payload: DecisionCreate, db: Session = Depends(get_db)):
    created_at = datetime.now(timezone.utc)
    prev_hash = get_latest_row_hash(db)

    row_hash = compute_row_hash(
        org_id=str(payload.org_id) if payload.org_id else "",
        user_id=str(payload.user_id),
        model_id=str(payload.model_id),
        category=payload.category,
        prompt_hash=payload.prompt_hash,
        recommendation_text=payload.recommendation_text,
        diff_ref=payload.diff_ref,
        created_at=created_at.isoformat(),
        prev_hash=prev_hash,
    )

    decision = Decision(
        id=uuid.uuid4(),
        org_id=payload.org_id,
        user_id=payload.user_id,
        model_id=payload.model_id,
        category=payload.category,
        prompt_hash=payload.prompt_hash,
        recommendation_text=payload.recommendation_text,
        diff_ref=payload.diff_ref,
        created_at=created_at,
        prev_hash=prev_hash,
        row_hash=row_hash,
    )

    db.add(decision)
    db.commit()
    db.refresh(decision)
    return decision


@router.get("/{decision_id}", response_model=DecisionResponse)
def get_decision(decision_id: uuid.UUID, db: Session = Depends(get_db)):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    return decision
