from datetime import datetime, timezone

from sqlalchemy.orm import Session

from db.models import Message


def _as_dict(message):
    return {
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


def load_conversation(
    user_id,
    db: Session,
):
    if not user_id:
        raise ValueError("user_id is required")

    messages = (
        db.query(Message)
        .filter(Message.user_id == user_id)
        .order_by(Message.created_at.asc(), Message.id.asc())
        .all()
    )

    return [_as_dict(message) for message in messages]


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

    db.commit()