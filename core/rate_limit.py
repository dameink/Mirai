"""Database-backed admission limits shared by API workers."""
import hashlib
import time

from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from db.database import Base, SessionLocal


class RequestLimit(Base):
    __tablename__ = "request_limits"
    key = Column(String(64), primary_key=True)
    count = Column(Integer, nullable=False)
    expires_at = Column(Float, nullable=False, index=True)


LIMITS = {
    "/content-reports": (10, 60),
    "/auth/account": (5, 60),
    "/auth/login": (20, 60),
    "/auth/register": (10, 3600),
    "/auth/forgot-password": (5, 60),
    "/auth/resend-verification": (5, 60),
    "/auth/verify-email": (20, 60),
    "/auth/reset-password": (20, 60),
    "/chat": (30, 60),
    "/notifications/test": (3, 60),
}


def admit_request(identity, path, now=None):
    limit, window = LIMITS[path]
    now = time.time() if now is None else now
    key = hashlib.sha256(f"{path}:{identity}".encode()).hexdigest()
    with SessionLocal() as db:
        dialect = db.bind.dialect.name
        insert = postgres_insert if dialect == "postgresql" else sqlite_insert
        db.query(RequestLimit).filter(RequestLimit.expires_at <= now).delete(synchronize_session=False)
        statement = insert(RequestLimit).values(key=key, count=1, expires_at=now + window)
        statement = statement.on_conflict_do_update(
            index_elements=[RequestLimit.key],
            set_={"count": RequestLimit.count + 1},
            where=RequestLimit.count < limit,
        )
        # psycopg may report rowcount=-1 for INSERT; RETURNING is portable.
        accepted = db.execute(statement.returning(RequestLimit.key)).scalar_one_or_none()
        db.commit()
        return accepted is not None
