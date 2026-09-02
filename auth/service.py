import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from auth.security import hash_password, verify_password, create_token
from db.models import User, Session as DBSession


ACCESS_TOKEN_MINUTES = 15
REFRESH_TOKEN_DAYS = 30


def _as_utc(value):
    if value is None:
        return None

    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


def _user_dict(user):
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at,
    }


def find_user_by_email(db: Session, email: str):
    normalized_email = email.strip().lower()

    return (
        db.query(User)
        .filter(User.email == normalized_email)
        .first()
    )


def find_user_by_id(db: Session, user_id: str):
    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )


def register_user(
    db: Session,
    email: str,
    password: str,
):
    normalized_email = email.strip().lower()

    if find_user_by_email(db, normalized_email):
        raise ValueError(
            "A user with this email already exists."
        )

    user = User(
        id=str(uuid.uuid4()),
        email=normalized_email,
        password_hash=hash_password(password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
):
    user = find_user_by_email(db, email)

    if user is None:
        return None

    if not verify_password(
        password,
        user.password_hash,
    ):
        return None

    return user


def create_auth_tokens(
    db: Session,
    user_id: str,
):
    now = datetime.now(timezone.utc)

    access_token = create_token()
    refresh_token = create_token()

    session = DBSession(
        id=str(uuid.uuid4()),
        user_id=user_id,
        access_token=access_token,
        refresh_token=refresh_token,
        created_at=now,
        access_expires_at=(
            now + timedelta(
                minutes=ACCESS_TOKEN_MINUTES
            )
        ),
        refresh_expires_at=(
            now + timedelta(
                days=REFRESH_TOKEN_DAYS
            )
        ),
        revoked=False,
    )

    db.add(session)
    db.commit()

    return access_token, refresh_token


def get_user_from_access_token(
    db: Session,
    access_token: str,
):
    session = (
        db.query(DBSession)
        .filter(
            DBSession.access_token == access_token,
        )
        .first()
    )

    if not session:
        return None

    if session.revoked:
        return None

    now = datetime.now(timezone.utc)

    expires_at = _as_utc(
        session.access_expires_at
    )

    if expires_at is None or expires_at <= now:
        return None

    user = find_user_by_id(
        db,
        session.user_id,
    )

    if not user:
        return None

    return _user_dict(user)


def get_session_by_refresh_token(
    db: Session,
    refresh_token: str,
):
    session = (
        db.query(DBSession)
        .filter(
            DBSession.refresh_token == refresh_token,
            DBSession.revoked == False,
        )
        .first()
    )

    if not session:
        return None

    now = datetime.now(timezone.utc)

    expires_at = _as_utc(
        session.refresh_expires_at
    )

    if expires_at is None or expires_at <= now:
        session.revoked = True
        db.commit()
        return None

    return session


def get_user_from_refresh_token(
    db: Session,
    refresh_token: str,
):
    session = get_session_by_refresh_token(
        db,
        refresh_token,
    )

    if not session:
        return None

    return find_user_by_id(
        db,
        session.user_id,
    )


def rotate_refresh_token(
    db: Session,
    old_refresh_token: str,
):
    session = get_session_by_refresh_token(
        db,
        old_refresh_token,
    )

    if not session:
        return None

    user_id = session.user_id

    session.revoked = True

    now = datetime.now(timezone.utc)

    access_token = create_token()
    new_refresh_token = create_token()

    new_session = DBSession(
        id=str(uuid.uuid4()),
        user_id=user_id,
        access_token=access_token,
        refresh_token=new_refresh_token,
        created_at=now,
        access_expires_at=(
            now + timedelta(
                minutes=ACCESS_TOKEN_MINUTES
            )
        ),
        refresh_expires_at=(
            now + timedelta(
                days=REFRESH_TOKEN_DAYS
            )
        ),
        revoked=False,
    )

    db.add(new_session)
    db.commit()

    return access_token, new_refresh_token


def revoke_refresh_token(
    db: Session,
    refresh_token: str,
):
    session = (
        db.query(DBSession)
        .filter(
            DBSession.refresh_token == refresh_token,
        )
        .first()
    )

    if not session:
        return False

    session.revoked = True
    db.commit()

    return True