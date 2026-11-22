"""Index knowledge fragments for lexical retrieval."""

from alembic import op

revision = "0009_knowledge_search"
down_revision = "0008_knowledge"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE INDEX knowledge_chunks_search ON knowledge_chunks USING gin (to_tsvector('simple', content))")


def downgrade():
    op.drop_index("knowledge_chunks_search", table_name="knowledge_chunks")
