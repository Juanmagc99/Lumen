"""Add persistent classification options and structured decisions."""

import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0004_classification_options"
down_revision = "0003_classification_claim"
branch_labels = None
depends_on = None


def upgrade():
    options = op.create_table(
        "classification_options",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("kind", sa.String(16), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.CheckConstraint("kind IN ('category', 'priority')", name="classification_option_kind"),
        sa.CheckConstraint("name ~ '[^[:space:]]'", name="classification_option_name"),
    )
    op.create_index(
        "classification_option_unique_name", "classification_options",
        ["kind", sa.text("lower(regexp_replace(name, '^[[:space:]]+|[[:space:]]+$', '', 'g'))")], unique=True,
    )
    op.bulk_insert(options, [
        {"id": uuid.uuid4(), "kind": kind, "name": name, "active": True}
        for kind, names in (
            ("category", ("Inquiry", "Incident", "Request", "Other")),
            ("priority", ("Low", "Normal", "High", "Urgent")),
        )
        for name in names
    ])
    op.add_column("classification_jobs", sa.Column("category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("classification_options.id")))
    op.add_column("classification_jobs", sa.Column("priority_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("classification_options.id")))
    op.add_column("classification_jobs", sa.Column("failure_reason", sa.String(32)))


def downgrade():
    # A model result with null IDs still represents two undetermined decisions.
    op.execute("""DO $$ BEGIN
        IF EXISTS (SELECT 1 FROM classification_jobs WHERE result_source = 'model' OR category_id IS NOT NULL OR priority_id IS NOT NULL) THEN
            RAISE EXCEPTION 'Structured classification decisions must be retained before downgrade';
        END IF;
    END $$""")
    op.drop_column("classification_jobs", "failure_reason")
    op.drop_column("classification_jobs", "priority_id")
    op.drop_column("classification_jobs", "category_id")
    op.drop_index("classification_option_unique_name", table_name="classification_options")
    op.drop_table("classification_options")
