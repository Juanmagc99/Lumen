"""Link visible responses to their adopted AI generation."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "0011_response_provenance"
down_revision = "0010_response_generation"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("ticket_responses", sa.Column("adopted_generation_id", UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("response_adopted_generation_fk", "ticket_responses", "response_generations", ["adopted_generation_id"], ["id"])


def downgrade():
    op.execute("""DO $$ BEGIN
        IF EXISTS (SELECT 1 FROM ticket_responses WHERE adopted_generation_id IS NOT NULL) THEN
            RAISE EXCEPTION 'Cannot discard response provenance';
        END IF;
    END $$""")
    op.drop_constraint("response_adopted_generation_fk", "ticket_responses", type_="foreignkey")
    op.drop_column("ticket_responses", "adopted_generation_id")
