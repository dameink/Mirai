"""Move user documents and idempotency receipts into the relational database."""
from alembic import op
import sqlalchemy as sa
revision = "0002_user_state"
down_revision = "0001_baseline"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("user_documents",
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("kind", sa.String(32), primary_key=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("source_digest", sa.String(64), nullable=True),
    )
    op.create_table("chat_receipts",
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("request_id", sa.String(64), primary_key=True),
        sa.Column("payload_hash", sa.String(64), nullable=False),
        sa.Column("response", sa.JSON(), nullable=False),
    )


def downgrade():
    raise RuntimeError("User state lives in this revision; restore a verified backup instead of dropping it")
