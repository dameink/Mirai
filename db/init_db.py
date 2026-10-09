"""Versioned schema upgrades; production upgrades run as a single deployment step."""
from pathlib import Path
from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from db.database import engine


def migration_config():
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    return config


def init_db(target_engine=None):
    config = migration_config()
    with (target_engine or engine).begin() as connection:
        config.attributes["connection"] = connection
        command.upgrade(config, "head")


def check_schema(target_engine=None):
    expected = ScriptDirectory.from_config(migration_config()).get_current_head()
    with (target_engine or engine).connect() as connection:
        actual = MigrationContext.configure(connection).get_current_revision()
    if actual != expected:
        raise RuntimeError("Database migration required: python -m db.manage upgrade")
    return actual


if __name__ == "__main__":
    init_db()
