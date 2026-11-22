"""Add tag colors and durable per-field manual selections."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0006_ticket_tags"
down_revision = "0005_ticket_responses"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("classification_options", sa.Column("color", sa.String(7), nullable=False, server_default="#64748B"))
    op.create_check_constraint("classification_option_color", "classification_options", "color ~ '^#[0-9A-Fa-f]{6}$'")
    op.add_column("tickets", sa.Column("manual_category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("classification_options.id")))
    op.add_column("tickets", sa.Column("manual_priority_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("classification_options.id")))
    op.add_column("tickets", sa.Column("classification_revision", sa.Integer(), nullable=False, server_default="0"))
    op.create_check_constraint("ticket_classification_revision", "tickets", "classification_revision >= 0")


def downgrade():
    op.execute("""DO $$ BEGIN
        IF EXISTS (SELECT 1 FROM tickets WHERE manual_category_id IS NOT NULL OR manual_priority_id IS NOT NULL)
           OR EXISTS (SELECT 1 FROM classification_options WHERE color <> '#64748B') THEN
            RAISE EXCEPTION 'Manual classification choices and tag colors must be retained before downgrade';
        END IF;
    END $$""")
    op.drop_constraint("ticket_classification_revision", "tickets", type_="check")
    op.drop_column("tickets", "classification_revision")
    op.drop_column("tickets", "manual_priority_id")
    op.drop_column("tickets", "manual_category_id")
    op.drop_constraint("classification_option_color", "classification_options", type_="check")
    op.drop_column("classification_options", "color")
