import hashlib
import json
from typing import Optional


def compute_row_hash(
    org_id: str,
    user_id: str,
    model_id: str,
    category: str,
    prompt_hash: str,
    recommendation_text: str,
    diff_ref: Optional[str],
    created_at: str,
    prev_hash: Optional[str],
) -> str:
    """
    Deterministically hash the content of a decision row together with
    the previous row hash, forming a tamper-evident chain.
    """
    payload = {
        "org_id": org_id,
        "user_id": user_id,
        "model_id": model_id,
        "category": category,
        "prompt_hash": prompt_hash,
        "recommendation_text": recommendation_text,
        "diff_ref": diff_ref,
        "created_at": created_at,
        "prev_hash": prev_hash,
    }
    serialized = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
from sqlalchemy.orm import Session

from app.models.decision import Decision


def get_latest_row_hash(db: Session) -> str | None:
    """Return the row_hash of the most recently created decision, or None if the ledger is empty."""
    latest = (
        db.query(Decision)
        .order_by(Decision.created_at.desc())
        .first()
    )
    return latest.row_hash if latest else None
