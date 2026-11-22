"""Add semantic indexing and retrieval audit without changing existing sources."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "0014_hybrid_retrieval"
down_revision = "0013_user_security"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "semantic_index_jobs",
        sa.Column("version_id", UUID(as_uuid=True), sa.ForeignKey("knowledge_versions.id"), primary_key=True),
        sa.Column("model", sa.Text(), primary_key=True),
        sa.Column("dimensions", sa.Integer(), primary_key=True),
        sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("claim_token", UUID(as_uuid=True)),
        sa.Column("claim_expires_at", sa.DateTime(timezone=True)),
        sa.Column("failure_reason", sa.String(255)),
        sa.Column("input_tokens", sa.BigInteger()),
        sa.CheckConstraint("dimensions > 0 AND dimensions <= 16000", name="semantic_index_dimensions"),
        sa.CheckConstraint("status IN ('pending', 'processing', 'ready', 'failed')", name="semantic_index_status"),
        sa.CheckConstraint("attempts >= 0", name="semantic_index_attempts"),
        sa.CheckConstraint("input_tokens IS NULL OR input_tokens >= 0", name="semantic_index_tokens"),
        sa.CheckConstraint("(status = 'processing' AND claim_token IS NOT NULL AND claim_expires_at IS NOT NULL) OR (status <> 'processing' AND claim_token IS NULL AND claim_expires_at IS NULL)", name="semantic_index_claim"),
    )
    op.execute("""
        CREATE TABLE knowledge_embeddings (
            chunk_id uuid NOT NULL REFERENCES knowledge_chunks(id),
            model text NOT NULL,
            dimensions integer NOT NULL CHECK (dimensions > 0 AND dimensions <= 16000),
            embedding vector NOT NULL,
            PRIMARY KEY (chunk_id, model, dimensions),
            CHECK (vector_dims(embedding) = dimensions)
        )
    """)
    op.add_column("response_attempts", sa.Column("retrieval_mode", sa.String(16)))
    op.add_column("response_attempts", sa.Column("retrieval_reason", sa.String(64)))
    op.add_column("response_attempts", sa.Column("embedding_input_tokens", sa.Integer()))
    op.create_check_constraint("response_attempt_retrieval_mode", "response_attempts", "retrieval_mode IS NULL OR retrieval_mode IN ('hybrid', 'lexical', 'none')")
    op.create_check_constraint("response_attempt_embedding_tokens", "response_attempts", "embedding_input_tokens IS NULL OR embedding_input_tokens >= 0")


def downgrade():
    op.execute("""DO $$ BEGIN
        IF EXISTS (SELECT 1 FROM response_attempts WHERE retrieval_mode IS NOT NULL) THEN
            RAISE EXCEPTION 'Cannot discard retained retrieval audit';
        END IF;
    END $$""")
    op.drop_constraint("response_attempt_embedding_tokens", "response_attempts", type_="check")
    op.drop_constraint("response_attempt_retrieval_mode", "response_attempts", type_="check")
    op.drop_column("response_attempts", "embedding_input_tokens")
    op.drop_column("response_attempts", "retrieval_reason")
    op.drop_column("response_attempts", "retrieval_mode")
    op.drop_table("knowledge_embeddings")
    op.drop_table("semantic_index_jobs")
