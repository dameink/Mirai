"""Hash existing session credentials and persist retryable erasure jobs."""
import hashlib
from alembic import op
import sqlalchemy as sa
revision = "0003_credentials_deletion"
down_revision = "0002_user_state"
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    sessions = sa.table("sessions", sa.column("id", sa.String), sa.column("access_token", sa.String), sa.column("refresh_token", sa.String))
    for row in connection.execute(sa.select(sessions)).mappings():
        values = {key: "sha256$" + hashlib.sha256(row[key].encode("utf-8")).hexdigest()
                  for key in ("access_token", "refresh_token") if not row[key].startswith("sha256$")}
        if values:
            connection.execute(sessions.update().where(sessions.c.id == row["id"]).values(**values))
    op.create_table("account_erasure_jobs", sa.Column("user_id", sa.String(36), primary_key=True))


def downgrade():
    raise RuntimeError("Credential hashing is irreversible; restore a verified backup instead")
