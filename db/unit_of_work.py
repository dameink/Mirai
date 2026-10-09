from contextlib import contextmanager
from contextvars import ContextVar
from sqlalchemy import select, text
from sqlalchemy.orm import Session

_current_session = ContextVar("mirai_state_session", default=None)


class AppSession(Session):
    def commit(self):
        if self.info.get("atomic_user_request"):
            self.flush()
        else:
            super().commit()


def current_session():
    return _current_session.get()


@contextmanager
def bind_session(db):
    token = _current_session.set(db)
    try:
        yield db
    finally:
        _current_session.reset(token)


def begin_user_transaction(db, user_id):
    from db.models import User
    db.rollback()  # discard the authentication read transaction before acquiring a write lock
    if db.bind.dialect.name == "sqlite":
        db.execute(text("BEGIN IMMEDIATE"))
    else:
        db.execute(text("SET LOCAL lock_timeout = '30s'"))
    user = db.execute(select(User.id).where(User.id == user_id).with_for_update()).scalar_one_or_none()
    if user is None:
        db.rollback()
        raise UserUnavailableError("User no longer exists")
    db.info["atomic_user_request"] = True


def finish_user_transaction(db, success):
    db.info.pop("atomic_user_request", None)
    if success:
        db.commit()
    else:
        db.rollback()


class UserUnavailableError(ValueError):
    pass


@contextmanager
def user_transaction(db, user_id):
    if db.info.get("atomic_user_request"):
        yield
        return
    try:
        begin_user_transaction(db, user_id)
        yield
        finish_user_transaction(db, True)
    except BaseException:
        finish_user_transaction(db, False)
        raise
