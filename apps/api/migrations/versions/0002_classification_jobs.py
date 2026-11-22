"""Add durable ticket classification jobs."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_classification_jobs"
down_revision = "0001_tickets"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "classification_jobs",
        sa.Column("ticket_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tickets.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("claim_token", postgresql.UUID(as_uuid=True)),
        sa.Column("claim_expires_at", sa.DateTime(timezone=True)),
        sa.Column("result", sa.Text()),
        sa.Column("result_source", sa.String(32)),
        sa.CheckConstraint("status IN ('pending', 'processing', 'completed', 'failed')", name="classification_status"),
        sa.CheckConstraint("attempts >= 0", name="classification_attempts"),
    )


def downgrade():
    op.drop_table("classification_jobs")
