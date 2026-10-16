import os

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, event
from db.unit_of_work import AppSession
from sqlalchemy.orm import declarative_base, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/mirai.db")

if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1,
    )
connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False, "timeout": 30}
    from pathlib import Path
    from sqlalchemy.engine import make_url
    filename = make_url(DATABASE_URL).database
    if filename and filename != ":memory:":
        Path(filename).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,  # Reconnect stale pooled connections after database sleep/restart.
    hide_parameters=True,  # SQL exception representations must not include user data.
)

SessionLocal = sessionmaker(
    class_=AppSession,
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


if engine.dialect.name == "sqlite":
    @event.listens_for(engine, "connect")
    def sqlite_foreign_keys(connection, record):
        connection.execute("PRAGMA foreign_keys=ON")


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()