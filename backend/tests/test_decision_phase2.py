import hashlib
import uuid
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from pydantic import ValidationError
from app.models.decision import Decision
from app.schemas.decision import DecisionCreate
from app.services.ledger import compute_row_hash, verify_ledger


USER_ID = uuid.UUID("00000000-0000-4000-8000-000000000001")
MODEL_ID = uuid.UUID("00000000-0000-4000-8000-000000000002")


def payload(**changes):
    source = dict(user_id=USER_ID, model_id=MODEL_ID, title="Fix SQL injection",
                  recommendation_text="Use a parameterized query for user lookup.",
                  diff_content="--- a/app.py\n+++ b/app.py\n", category="injection",
                  affected_files=["app.py"])
    source.update(changes)
    return source


def decision(previous=None):
    item = Decision(id=uuid.uuid4(), user_id=USER_ID, model_id=MODEL_ID,
                    title="Fix SQL injection", category="injection",
                    prompt_hash=hashlib.sha256(b"prompt").hexdigest(),
                    recommendation_text="Use a parameterized query for user lookup.",
                    diff_content="--- a/app.py\n+++ b/app.py\n",
                    affected_files=["app.py"], status="captured", hash_version=3,
                    created_at=datetime.now(timezone.utc), prev_hash=previous)
    item.row_hash = compute_row_hash(item)
    return item


class FakeQuery:
    def __init__(self, rows): self.rows = rows
    def order_by(self, *args): return self
    def yield_per(self, count): return self.rows


class FakeSession:
    def __init__(self, rows): self.rows = rows
    def query(self, model): return FakeQuery(self.rows)


def test_decision_input_normalizes_paths_and_preserves_diff():
    diff = " --- a/app.py\n+++ b/app.py\n"
    result = DecisionCreate.model_validate(payload(diff_content=diff, affected_files=["b.py", "a.py", "b.py"]))
    assert result.diff_content == diff
    assert result.affected_files == ["a.py", "b.py"]


@pytest.mark.parametrize("path", ["../secret", "/etc/passwd", "a/../../b", "a//b"])
def test_decision_rejects_unsafe_paths(path):
    with pytest.raises(ValidationError):
        DecisionCreate.model_validate(payload(affected_files=[path]))


def test_ledger_detects_modified_history_and_broken_link():
    first = decision()
    second = decision(first.row_hash)
    assert verify_ledger(FakeSession([first, second])) == {"valid": True, "checked": 2, "broken_at": None}
    first.recommendation_text = "tampered recommendation"
    assert verify_ledger(FakeSession([first, second]))["broken_at"] == str(first.id)
    first.recommendation_text = "Use a parameterized query for user lookup."
    second.prev_hash = "invalid"
    assert verify_ledger(FakeSession([first, second]))["broken_at"] == str(second.id)


def test_stage_can_change_without_rewriting_capture_hash():
    item = decision()
    original = item.row_hash
    item.status = "tested"
    assert compute_row_hash(item) == original
