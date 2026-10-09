"""Adopt existing installations without dropping data."""
from alembic import op
import sqlalchemy as sa
from db.migrations.baseline import Base
revision = "0001_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind, checkfirst=True)
    columns = {c["name"] for c in sa.inspect(bind).get_columns("users")}
    if "email_verified" not in columns:
        op.add_column("users", sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.false()))
    if "notifications_enabled" not in columns:
        op.add_column("users", sa.Column("notifications_enabled", sa.Boolean(), nullable=False, server_default=sa.true()))


def downgrade():
    raise RuntimeError("Baseline adoption cannot be undone destructively; restore a verified backup")
