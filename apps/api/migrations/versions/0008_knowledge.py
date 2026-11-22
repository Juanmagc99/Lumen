"""Add versioned knowledge and durable ingestion jobs."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "0008_knowledge"
down_revision = "0007_multiple_categories"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "knowledge_bases",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("name ~ '[^[:space:]]'", name="knowledge_base_name"),
    )
    op.create_table(
        "knowledge_documents",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("knowledge_base_id", UUID(as_uuid=True), sa.ForeignKey("knowledge_bases.id"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("name ~ '[^[:space:]]'", name="knowledge_document_name"),
    )
    op.create_index("ix_knowledge_documents_knowledge_base_id", "knowledge_documents", ["knowledge_base_id"])
    op.create_table(
        "knowledge_versions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("document_id", UUID(as_uuid=True), sa.ForeignKey("knowledge_documents.id"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("version > 0", name="knowledge_version_number"),
        sa.CheckConstraint("content ~ '[^[:space:]]'", name="knowledge_version_content"),
    )
    op.create_index("knowledge_version_unique", "knowledge_versions", ["document_id", "version"], unique=True)
    op.create_table(
        "knowledge_chunks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("version_id", UUID(as_uuid=True), sa.ForeignKey("knowledge_versions.id"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
    )
    op.create_index("knowledge_chunk_unique", "knowledge_chunks", ["version_id", "position"], unique=True)
    op.create_table(
        "ingestion_jobs",
        sa.Column("version_id", UUID(as_uuid=True), sa.ForeignKey("knowledge_versions.id"), primary_key=True),
        sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("claim_token", UUID(as_uuid=True)),
        sa.Column("claim_expires_at", sa.DateTime(timezone=True)),
        sa.Column("failure_reason", sa.String(255)),
        sa.CheckConstraint("status IN ('pending', 'processing', 'ready', 'failed')", name="ingestion_status"),
        sa.CheckConstraint("attempts >= 0", name="ingestion_attempts"),
        sa.CheckConstraint("(status = 'processing' AND claim_token IS NOT NULL AND claim_expires_at IS NOT NULL) OR (status <> 'processing' AND claim_token IS NULL AND claim_expires_at IS NULL)", name="ingestion_claim"),
    )


def downgrade():
    op.execute("""DO $$ BEGIN
        IF EXISTS (SELECT 1 FROM knowledge_bases) THEN
            RAISE EXCEPTION 'Cannot discard retained knowledge; remove it explicitly before downgrading';
        END IF;
    END $$""")
    op.drop_table("ingestion_jobs")
    op.drop_table("knowledge_chunks")
    op.drop_table("knowledge_versions")
    op.drop_table("knowledge_documents")
    op.drop_table("knowledge_bases")
