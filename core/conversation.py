from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from db.models import Message, ChatReceipt
from sqlalchemy import JSON


def _as_dict(message):
    return {
        "id": message.id,
        "role": message.role,
        "content": message.content,
        "timestamp": message.created_at.isoformat(),
    }


def add_message(
    role,
    content,
    user_id,
    db: Session,
):
    if not user_id:
        raise ValueError("user_id is required")

    message = Message(
        user_id=user_id,
        role=role,
        content=content,
        created_at=datetime.now(timezone.utc),
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return _as_dict(message)


def load_conversation(user_id, db: Session, limit=None, before_id=None):
    if not user_id:
        raise ValueError("user_id is required")
    query = db.query(Message).filter(Message.user_id == user_id)
    if before_id:
        cursor = query.filter(Message.id == before_id).first()
        if cursor is None:
            return []
        query = query.filter(or_(
            Message.created_at < cursor.created_at,
            and_(Message.created_at == cursor.created_at, Message.id < cursor.id),
        ))
    query = query.order_by(Message.created_at.desc(), Message.id.desc())
    if limit is not None:
        query = query.limit(limit)
    return [_as_dict(message) for message in reversed(query.all())]


def add_exchange(user_id, user_content, assistant_content, db: Session):
    """Both sides of a successful turn are saved in one database transaction."""
    for role, content in (("user", user_content), ("assistant", assistant_content)):
        db.add(Message(user_id=user_id, role=role, content=content, created_at=datetime.now(timezone.utc)))
    db.commit()


def save_conversation(
    conversation,
    user_id,
    db: Session,
):
    """
    Replace the user's conversation in the database.

    Used mainly for reset/import compatibility.
    """
    if not user_id:
        raise ValueError("user_id is required")

    (
        db.query(Message)
        .filter(Message.user_id == user_id)
        .delete(synchronize_session=False)
    )

    for item in conversation:
        created_at = item.get("timestamp")

        if created_at:
            try:
                parsed_time = datetime.fromisoformat(created_at)
                if parsed_time.tzinfo is None:
                    parsed_time = parsed_time.replace(tzinfo=timezone.utc)
            except ValueError:
                parsed_time = datetime.now(timezone.utc)
        else:
            parsed_time = datetime.now(timezone.utc)

        db.add(
            Message(
                user_id=user_id,
                role=item["role"],
                content=item["content"],
                created_at=parsed_time,
            )
        )

    db.commit()


def get_history(
    limit=10,
    user_id=None,
    db: Session = None,
):
    if not user_id:
        raise ValueError("user_id is required")

    messages = (
        db.query(Message)
        .filter(Message.user_id == user_id)
        .order_by(Message.created_at.desc(), Message.id.desc())
        .limit(limit)
        .all()
    )

    messages.reverse()

    return [_as_dict(message) for message in messages]


def clear_conversation(
    user_id,
    db: Session,
):
    if not user_id:
        raise ValueError("user_id is required")

    (
        db.query(Message)
        .filter(Message.user_id == user_id)
        .delete(synchronize_session=False)
    )

    # Keep the request key as a tombstone, but erase cached private response/state.
    db.query(ChatReceipt).filter(ChatReceipt.user_id == user_id).update(
        {ChatReceipt.response: JSON.NULL}, synchronize_session=False,
    )

    db.commit()