"""Add canonical decision capture fields and demo catalog.

Revision ID: 2a01_decision_capture
Revises: 9d4e60fb7c76
"""
import uuid
from datetime import datetime, timezone
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "2a01_decision_capture"
down_revision = "9d4e60fb7c76"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("ai_models", sa.Column("created_at", sa.DateTime(timezone=True), nullable=True))
    op.execute("UPDATE ai_models SET created_at = now() WHERE created_at IS NULL")
    op.alter_column("ai_models", "created_at", nullable=False)
    op.add_column("decisions", sa.Column("title", sa.String(length=200), nullable=True))
    op.add_column("decisions", sa.Column("diff_content", sa.Text(), nullable=True))
    op.add_column("decisions", sa.Column("affected_files", JSONB(), nullable=True))
    op.add_column("decisions", sa.Column("status", sa.String(length=32), nullable=True))
    op.add_column("decisions", sa.Column("hash_version", sa.Integer(), nullable=True))
    op.execute("UPDATE decisions SET title = left(recommendation_text, 200), affected_files = '[]'::jsonb, status = 'captured', hash_version = 1")
    op.alter_column("decisions", "affected_files", nullable=False)
    op.alter_column("decisions", "status", nullable=False)
    op.alter_column("decisions", "hash_version", nullable=False)
    op.create_index("ix_decisions_created_at", "decisions", ["created_at"])
    op.create_index("ix_decisions_category", "decisions", ["category"])
    op.create_index("ix_decisions_model_id", "decisions", ["model_id"])
    op.create_index("ix_decisions_status", "decisions", ["status"])
    users = sa.table("users", sa.column("id", sa.UUID()), sa.column("email", sa.String()), sa.column("role", sa.String()))
    models = sa.table("ai_models", sa.column("id", sa.UUID()), sa.column("provider", sa.String()), sa.column("model_name", sa.String()), sa.column("version", sa.String()), sa.column("created_at", sa.DateTime(timezone=True)))
    op.bulk_insert(users, [{"id": uuid.UUID("00000000-0000-4000-8000-000000000001"), "email": "demo@aegis.local", "role": "developer"}])
    op.bulk_insert(models, [{"id": uuid.UUID("00000000-0000-4000-8000-000000000002"), "provider": "Demo", "model_name": "Example AI recommendation", "version": "1", "created_at": datetime.now(timezone.utc)}])


def downgrade() -> None:
    op.execute("DELETE FROM ai_models WHERE id = '00000000-0000-4000-8000-000000000002' AND NOT EXISTS (SELECT 1 FROM decisions WHERE model_id = '00000000-0000-4000-8000-000000000002')")
    op.execute("DELETE FROM users WHERE id = '00000000-0000-4000-8000-000000000001' AND NOT EXISTS (SELECT 1 FROM decisions WHERE user_id = '00000000-0000-4000-8000-000000000001')")
    op.drop_index("ix_decisions_status", table_name="decisions")
    op.drop_index("ix_decisions_model_id", table_name="decisions")
    op.drop_index("ix_decisions_category", table_name="decisions")
    op.drop_index("ix_decisions_created_at", table_name="decisions")
    for name in ("hash_version", "status", "affected_files", "diff_content", "title"):
        op.drop_column("decisions", name)
    op.drop_column("ai_models", "created_at")
