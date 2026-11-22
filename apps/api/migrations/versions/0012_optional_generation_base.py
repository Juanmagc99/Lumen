"""Allow explicit response generation without a knowledge base."""

from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision = "0012_optional_generation_base"
down_revision = "0011_response_provenance"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("response_generations", "knowledge_base_id", existing_type=UUID(as_uuid=True), nullable=True)


def downgrade():
    op.execute("""DO $$ BEGIN
        IF EXISTS (SELECT 1 FROM response_generations WHERE knowledge_base_id IS NULL) THEN
            RAISE EXCEPTION 'Cannot discard generations without a knowledge base';
        END IF;
    END $$""")
    op.alter_column("response_generations", "knowledge_base_id", existing_type=UUID(as_uuid=True), nullable=False)
