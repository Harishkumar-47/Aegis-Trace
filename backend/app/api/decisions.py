import hashlib
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models.ai_model import AIModel
from app.models.user import User
from app.models.decision import Decision
from app.schemas.decision import Category, DecisionCreate, DecisionPage, DecisionResponse
from app.services.ledger import compute_row_hash, get_previous_hash, lock_ledger, verify_ledger

router = APIRouter(prefix="/api/decisions", tags=["decisions"])


def serialize(decision: Decision) -> DecisionResponse:
    result = DecisionResponse.model_validate(decision)
    result.model_name = decision.model.model_name if decision.model else None
    return result


@router.post("", response_model=DecisionResponse, status_code=status.HTTP_201_CREATED)
def create_decision(payload: DecisionCreate, db: Session = Depends(get_db)):
    if not db.get(User, payload.user_id):
        raise HTTPException(422, "Unknown user_id")
    if not db.get(AIModel, payload.model_id):
        raise HTTPException(422, "Unknown model_id")
    created_at = datetime.now(timezone.utc)
    decision = Decision(
        id=uuid.uuid4(), org_id=payload.organization_id, user_id=payload.user_id,
        model_id=payload.model_id, title=payload.title, category=payload.category.value,
        prompt_hash=hashlib.sha256((payload.prompt or "").encode("utf-8")).hexdigest(),
        recommendation_text=payload.recommendation_text, diff_content=payload.diff_content,
        affected_files=payload.affected_files, status="captured", hash_version=3,
        created_at=created_at,
    )
    try:
        lock_ledger(db)
        if not verify_ledger(db)["valid"]:
            raise HTTPException(409, "Decision ledger integrity check failed")
        decision.prev_hash = get_previous_hash(db)
        decision.row_hash = compute_row_hash(decision)
        db.add(decision)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(422, "Decision references invalid data") from exc
    db.refresh(decision)
    return serialize(decision)


@router.get("", response_model=DecisionPage)
def list_decisions(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    category: Category | None = None, model_id: uuid.UUID | None = None,
    status_filter: str | None = Query(None, alias="status"),
    search: str | None = Query(None, max_length=200), db: Session = Depends(get_db),
):
    query = db.query(Decision).options(joinedload(Decision.model))
    if category:
        query = query.filter(Decision.category == category.value)
    if model_id:
        query = query.filter(Decision.model_id == model_id)
    if status_filter:
        query = query.filter(Decision.status == status_filter)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(or_(Decision.title.ilike(term), Decision.recommendation_text.ilike(term)))
    total = query.count()
    items = query.order_by(Decision.created_at.desc(), Decision.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return DecisionPage(items=[serialize(item) for item in items], page=page, page_size=page_size, total=total)


@router.get("/{decision_id}", response_model=DecisionResponse)
def get_decision(decision_id: uuid.UUID, db: Session = Depends(get_db)):
    decision = db.query(Decision).options(joinedload(Decision.model)).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(404, "Decision not found")
    return serialize(decision)
