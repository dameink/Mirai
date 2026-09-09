import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from db.models import EmailVerification


CODE_LENGTH = 6
CODE_EXPIRE_MINUTES = 10
MAX_ATTEMPTS = 5


def _hash_code(code: str) -> str:
    return hashlib.sha256(
        code.encode("utf-8")
    ).hexdigest()


def generate_verification_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def create_verification_code(
    db: Session,
    user_id: str,
):
    code = generate_verification_code()

    verification = EmailVerification(
        user_id=user_id,
        code_hash=_hash_code(code),
        expires_at=(
            datetime.now(timezone.utc)
            + timedelta(minutes=CODE_EXPIRE_MINUTES)
        ),
        attempts=0,
        used=False,
    )

    db.add(verification)
    db.commit()
    db.refresh(verification)

    return code


def verify_code(
    db: Session,
    user_id: str,
    code: str,
):
    verification = (
        db.query(EmailVerification)
        .filter(
            EmailVerification.user_id == user_id,
            EmailVerification.used == False,
        )
        .order_by(
            EmailVerification.created_at.desc()
        )
        .first()
    )

    if verification is None:
        return False

    now = datetime.now(timezone.utc)

    expires_at = verification.expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )

    if expires_at <= now:
        return False

    if verification.attempts >= MAX_ATTEMPTS:
        return False

    verification.attempts += 1

    if verification.code_hash != _hash_code(code):
        db.commit()
        return False

    verification.used = True

    db.commit()

    return True

RESEND_COOLDOWN_SECONDS = 60


def can_resend_verification_code(
    db: Session,
    user_id: str,
):
    verification = (
        db.query(EmailVerification)
        .filter(
            EmailVerification.user_id == user_id,
        )
        .order_by(
            EmailVerification.created_at.desc()
        )
        .first()
    )

    if verification is None:
        return True

    created_at = verification.created_at

    if created_at.tzinfo is None:
        created_at = created_at.replace(
            tzinfo=timezone.utc
        )

    now = datetime.now(timezone.utc)

    elapsed = (
        now - created_at
    ).total_seconds()

    return elapsed >= RESEND_COOLDOWN_SECONDS

def resend_verification_code(
    db: Session,
    user_id: str,
):
    if not can_resend_verification_code(db, user_id):
        return None

    previous_codes = (
        db.query(EmailVerification)
        .filter(
            EmailVerification.user_id == user_id,
            EmailVerification.used == False,
        )
        .all()
    )

    for verification in previous_codes:
        verification.used = True

    db.commit()

    return create_verification_code(
        db,
        user_id,
    )