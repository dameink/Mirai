from alembic import context
from db.database import Base, engine
from db import models
from core import rate_limit


def run(connection):
    context.configure(connection=connection, target_metadata=Base.metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    raise RuntimeError("Use online migrations against a backup/staging database first")
provided = context.config.attributes.get("connection")
if provided is not None:
    run(provided)
else:
    with engine.connect() as connection:
        run(connection)
