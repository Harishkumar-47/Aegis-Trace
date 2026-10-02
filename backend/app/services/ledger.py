"""Deterministic hash chain for immutable decision evidence."""
import hashlib
import json
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.models.decision import Decision


def compute_row_hash(decision: Decision) -> str:
    if decision.hash_version == 1:
        # Original canonical form, retained so existing development records remain verifiable.
        payload = {
            "org_id": str(decision.org_id) if decision.org_id else "",
            "user_id": str(decision.user_id),
            "model_id": str(decision.model_id),
            "category": decision.category,
            "prompt_hash": decision.prompt_hash,
            "recommendation_text": decision.recommendation_text,
            "diff_ref": decision.diff_ref,
            "created_at": decision.created_at.isoformat(),
            "prev_hash": decision.prev_hash,
        }
        serialized = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    payload = {
        "version": decision.hash_version, "id": str(decision.id),
        "organization_id": str(decision.org_id) if decision.org_id else None,
        "user_id": str(decision.user_id), "model_id": str(decision.model_id),
        "title": decision.title, "category": decision.category,
        "prompt_hash": decision.prompt_hash,
        "recommendation_text": decision.recommendation_text,
        "diff_content": decision.diff_content,
        "affected_files": decision.affected_files,
        **({"status": decision.status} if decision.hash_version == 2 else {}),
        "created_at": decision.created_at.isoformat(),
        "prev_hash": decision.prev_hash,
    }
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def lock_ledger(db: Session) -> None:
    # PostgreSQL transaction lock serializes writers across API workers.
    db.execute(text("SELECT pg_advisory_xact_lock(271828182)"))


def get_previous_hash(db: Session) -> str | None:
    latest = db.query(Decision).order_by(Decision.created_at.desc(), Decision.id.desc()).first()
    return latest.row_hash if latest else None


def verify_ledger(db: Session) -> dict:
    previous = None
    checked = 0
    for decision in db.query(Decision).order_by(Decision.created_at, Decision.id).yield_per(100):
        checked += 1
        if decision.prev_hash != previous or compute_row_hash(decision) != decision.row_hash:
            return {"valid": False, "checked": checked, "broken_at": str(decision.id)}
        previous = decision.row_hash
    return {"valid": True, "checked": checked, "broken_at": None}
