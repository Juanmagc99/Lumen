"""Store one manually reviewed response per ticket."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0005_ticket_responses"
down_revision = "0004_classification_options"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "ticket_responses",
        sa.Column("ticket_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tickets.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("edited_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.CheckConstraint("text ~ '[^[:space:]]'", name="ticket_response_text"),
        sa.CheckConstraint("status IN ('draft', 'approved')", name="ticket_response_status"),
        sa.CheckConstraint("revision > 0", name="ticket_response_revision"),
    )


def downgrade():
    op.execute("""DO $$ BEGIN
        IF EXISTS (SELECT 1 FROM ticket_responses) THEN
            RAISE EXCEPTION 'Response data must be retained before downgrade';
        END IF;
    END $$""")
    op.drop_table("ticket_responses")
