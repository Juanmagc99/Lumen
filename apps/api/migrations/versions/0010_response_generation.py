"""Persist response requests, attempts and shared model-call reservations."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = "0010_response_generation"
down_revision = "0009_knowledge_search"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "response_generations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("ticket_id", UUID(as_uuid=True), sa.ForeignKey("tickets.id"), nullable=False),
        sa.Column("knowledge_base_id", UUID(as_uuid=True), sa.ForeignKey("knowledge_bases.id"), nullable=False),
        sa.Column("subject", sa.Text(), nullable=False), sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="queued"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("claim_token", UUID(as_uuid=True)), sa.Column("claim_expires_at", sa.DateTime(timezone=True)),
        sa.Column("original_text", sa.Text()), sa.Column("rationale", sa.Text()),
        sa.Column("insufficient_evidence", sa.Boolean()), sa.Column("failure_reason", sa.String(64)),
        sa.CheckConstraint("status IN ('queued', 'running', 'completed', 'failed')", name="response_generation_status"),
        sa.CheckConstraint("attempts >= 0", name="response_generation_attempts"),
        sa.CheckConstraint("(status = 'running' AND claim_token IS NOT NULL AND claim_expires_at IS NOT NULL) OR (status <> 'running' AND claim_token IS NULL AND claim_expires_at IS NULL)", name="response_generation_claim"),
    )
    op.create_index("response_generation_active_ticket", "response_generations", ["ticket_id"], unique=True, postgresql_where=sa.text("status IN ('queued', 'running')"))
    op.create_table(
        "response_attempts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("generation_id", UUID(as_uuid=True), sa.ForeignKey("response_generations.id"), nullable=False),
        sa.Column("claim_token", UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("requested_model", sa.Text()), sa.Column("reported_model", sa.Text()), sa.Column("provider", sa.Text()),
        sa.Column("config_version", sa.String(64), nullable=False),
        sa.Column("sources", JSONB(), nullable=False), sa.Column("citations", JSONB()),
        sa.Column("provider_request_id", sa.Text()), sa.Column("input_tokens", sa.Integer()), sa.Column("output_tokens", sa.Integer()),
        sa.Column("estimated_cost", sa.Numeric(20, 8)), sa.Column("currency", sa.String(3)), sa.Column("pricing_basis", sa.Text()),
        sa.Column("failure_reason", sa.String(64)),
    )
    op.create_index("response_attempt_generation", "response_attempts", ["generation_id", "started_at"])
    op.create_table(
        "response_call_reservations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("attempt_id", UUID(as_uuid=True), sa.ForeignKey("response_attempts.id"), nullable=False, unique=True),
        sa.Column("reserved_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False), sa.Column("released_at", sa.DateTime(timezone=True)),
    )


def downgrade():
    op.execute("""DO $$ BEGIN
        IF EXISTS (SELECT 1 FROM response_generations) THEN
            RAISE EXCEPTION 'Cannot discard retained generation audit';
        END IF;
    END $$""")
    op.drop_table("response_call_reservations")
    op.drop_table("response_attempts")
    op.drop_table("response_generations")
