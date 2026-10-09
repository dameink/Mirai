import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from db.models import PasswordReset


CODE_LENGTH = 6
CODE_EXPIRE_MINUTES = 10
MAX_ATTEMPTS = 5
RESEND_COOLDOWN_SECONDS = 60


def _hash_code(code: str) -> str:
    return hashlib.sha256(
        code.encode("utf-8")
    ).hexdigest()


def generate_reset_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def create_reset_code(
    db: Session,
    user_id: str,
):
    from db.models import User
    db.query(User).filter(User.id == user_id).with_for_update().first()
    db.query(PasswordReset).filter(
        PasswordReset.user_id == user_id, PasswordReset.used == False,
    ).update({"used": True}, synchronize_session=False)
    code = generate_reset_code()

    reset = PasswordReset(
        user_id=user_id,
        code_hash=_hash_code(code),
        expires_at=(
            datetime.now(timezone.utc)
            + timedelta(minutes=CODE_EXPIRE_MINUTES)
        ),
        attempts=0,
        used=False,
    )

    db.add(reset)
    db.commit()
    db.refresh(reset)

    return code


def verify_reset_code(
    db: Session,
    user_id: str,
    code: str,
    commit: bool = True,
):
    reset = (
        db.query(PasswordReset)
        .filter(
            PasswordReset.user_id == user_id,
            PasswordReset.used == False,
        )
        .order_by(
            PasswordReset.created_at.desc()
        )
        .first()
    )

    if reset is None:
        return False

    now = datetime.now(timezone.utc)

    expires_at = reset.expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )

    if expires_at <= now:
        return False

    if reset.attempts >= MAX_ATTEMPTS:
        return False

    matched = secrets.compare_digest(reset.code_hash, _hash_code(code))
    claimed = db.query(PasswordReset).filter(
        PasswordReset.id == reset.id,
        PasswordReset.used == False,
        PasswordReset.attempts < MAX_ATTEMPTS,
    ).update({
        PasswordReset.attempts: PasswordReset.attempts + 1,
        PasswordReset.used: matched,
    }, synchronize_session=False)
    if not matched or not claimed:
        db.commit()
        return False
    db.query(PasswordReset).filter(
        PasswordReset.user_id == user_id,
        PasswordReset.used == False,
    ).update({"used": True}, synchronize_session=False)
    if commit:
        db.commit()
    return True


def can_resend_reset_code(
    db: Session,
    user_id: str,
):
    reset = (
        db.query(PasswordReset)
        .filter(
            PasswordReset.user_id == user_id,
        )
        .order_by(
            PasswordReset.created_at.desc()
        )
        .first()
    )

    if reset is None:
        return True

    created_at = reset.created_at

    if created_at.tzinfo is None:
        created_at = created_at.replace(
            tzinfo=timezone.utc
        )

    now = datetime.now(timezone.utc)

    elapsed = (
        now - created_at
    ).total_seconds()

    return elapsed >= RESEND_COOLDOWN_SECONDS


def resend_reset_code(
    db: Session,
    user_id: str,
):
    from db.models import User
    db.query(User).filter(User.id == user_id).with_for_update().first()
    if not can_resend_reset_code(db, user_id):
        return None

    return create_reset_code(
        db,
        user_id,
    )