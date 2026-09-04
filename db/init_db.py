from sqlalchemy import inspect, text

from db.database import Base, engine
from db import models


def init_db():
    # Create tables that do not exist yet
    Base.metadata.create_all(bind=engine)

    # Add columns that may be missing from existing databases
    inspector = inspect(engine)

    users_columns = {
        column["name"]
        for column in inspector.get_columns("users")
    }

    if "notifications_enabled" not in users_columns:
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    ALTER TABLE users
                    ADD COLUMN notifications_enabled
                    BOOLEAN NOT NULL DEFAULT TRUE
                    """
                )
            )

        print("Added users.notifications_enabled")


if __name__ == "__main__":
    init_db()
    print("Database initialized.")