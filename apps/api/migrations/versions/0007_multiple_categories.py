"""Store model and manual category sets independently."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0007_multiple_categories"
down_revision = "0006_ticket_tags"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("tickets", sa.Column("manual_categories_override", sa.Boolean(), nullable=False, server_default=sa.false()))
    for table in ("ticket_manual_categories", "classification_job_categories"):
        parent = "tickets.id" if table == "ticket_manual_categories" else "classification_jobs.ticket_id"
        op.create_table(
            table,
            sa.Column("ticket_id", postgresql.UUID(as_uuid=True), sa.ForeignKey(parent, ondelete="CASCADE"), primary_key=True),
            sa.Column("category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("classification_options.id"), primary_key=True),
        )
    op.execute("INSERT INTO ticket_manual_categories SELECT id, manual_category_id FROM tickets WHERE manual_category_id IS NOT NULL")
    op.execute("UPDATE tickets SET manual_categories_override = true WHERE manual_category_id IS NOT NULL")
    op.execute("INSERT INTO classification_job_categories SELECT ticket_id, category_id FROM classification_jobs WHERE category_id IS NOT NULL")
    op.drop_constraint("tickets_manual_category_id_fkey", "tickets", type_="foreignkey")
    op.drop_column("tickets", "manual_category_id")
    op.drop_constraint("classification_jobs_category_id_fkey", "classification_jobs", type_="foreignkey")
    op.drop_column("classification_jobs", "category_id")


def downgrade():
    op.execute("""DO $$ BEGIN
        IF EXISTS (SELECT ticket_id FROM ticket_manual_categories GROUP BY ticket_id HAVING count(*) > 1)
           OR EXISTS (SELECT ticket_id FROM classification_job_categories GROUP BY ticket_id HAVING count(*) > 1)
           OR EXISTS (SELECT 1 FROM tickets t WHERE t.manual_categories_override AND NOT EXISTS
                      (SELECT 1 FROM ticket_manual_categories c WHERE c.ticket_id = t.id)) THEN
            RAISE EXCEPTION 'Multiple or empty manual category selections cannot be retained by the older schema';
        END IF;
    END $$""")
    op.add_column("tickets", sa.Column("manual_category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("classification_options.id")))
    op.add_column("classification_jobs", sa.Column("category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("classification_options.id")))
    op.execute("UPDATE tickets t SET manual_category_id = c.category_id FROM ticket_manual_categories c WHERE c.ticket_id = t.id")
    op.execute("UPDATE classification_jobs j SET category_id = c.category_id FROM classification_job_categories c WHERE c.ticket_id = j.ticket_id")
    op.drop_table("classification_job_categories")
    op.drop_table("ticket_manual_categories")
    op.drop_column("tickets", "manual_categories_override")
