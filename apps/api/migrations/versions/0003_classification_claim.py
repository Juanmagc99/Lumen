"""Enforce consistent classification claims."""

from alembic import op

revision = "0003_classification_claim"
down_revision = "0002_classification_jobs"
branch_labels = None
depends_on = None


def upgrade():
    op.create_check_constraint(
        "classification_claim", "classification_jobs",
        "(status = 'processing' AND claim_token IS NOT NULL AND claim_expires_at IS NOT NULL) OR (status <> 'processing' AND claim_token IS NULL AND claim_expires_at IS NULL)",
    )


def downgrade():
    op.drop_constraint("classification_claim", "classification_jobs", type_="check")
