"""User-owned state documents backed by the current request transaction."""
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from db.database import SessionLocal
from db.models import User, UserDocument
from db.unit_of_work import current_session
from core.persistence import StateCorruptedError

FILES = {"emotion": "emotion.json", "relationship": "relationship.json",
         "learning_memory": "learning_memory.json", "learning_sessions": "learning_sessions.json"}


@contextmanager
def session_scope(db=None):
    active = db if db is not None else current_session()
    if active is not None:
        yield active
    else:
        with SessionLocal() as owned:
            yield owned
            owned.commit()


def read_document(user_id, kind, default, db=None):
    from core.user_state import BASE_DIR
    with session_scope(db) as session:
        record = session.get(UserDocument, (user_id, kind))
        if record is None:
            filename = FILES.get(kind)
            if filename and (Path(BASE_DIR) / str(user_id) / filename).exists():
                raise StateCorruptedError("Legacy state requires import: python -m db.manage import-state --apply")
            if session.get(User, user_id) is None:
                raise ValueError("Unknown user")
            insert = pg_insert if session.bind.dialect.name == "postgresql" else sqlite_insert
            session.execute(insert(UserDocument).values(user_id=user_id, kind=kind, payload=deepcopy(default)).on_conflict_do_nothing())
            session.flush()
            record = session.get(UserDocument, (user_id, kind))
        return deepcopy(record.payload)


def write_document(user_id, kind, payload, db=None):
    with session_scope(db) as session:
        insert = pg_insert if session.bind.dialect.name == "postgresql" else sqlite_insert
        statement = insert(UserDocument).values(user_id=user_id, kind=kind, payload=deepcopy(payload))
        session.execute(statement.on_conflict_do_update(
            index_elements=[UserDocument.user_id, UserDocument.kind],
            set_={"payload": statement.excluded.payload, "source_digest": None},
        ))
        session.flush()
        # Core reads use detached copies; expire only the affected ORM document if cached.
        record = session.get(UserDocument, (user_id, kind))
        if record is not None:
            session.expire(record)
