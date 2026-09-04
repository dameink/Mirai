from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from db.models import Message, Notification
from core.memory import get_memory
from core.relationship import get_relationship
from core.emotion import get_emotion


def _now():
    return datetime.now(timezone.utc)


def _utc(dt):
    if dt is None:
        return None

    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)

    return dt


def get_last_user_message(
    db: Session,
    user_id: str,
):
    return (
        db.query(Message)
        .filter(
            Message.user_id == user_id,
            Message.role == "user",
        )
        .order_by(
            Message.created_at.desc(),
            Message.id.desc(),
        )
        .first()
    )


def get_notification_stats(
    db: Session,
    user_id: str,
):
    now = _now()

    day_start = now - timedelta(days=1)
    week_start = now - timedelta(days=7)

    notifications_today = (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.sent_at >= day_start,
        )
        .count()
    )

    notifications_this_week = (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.sent_at >= week_start,
        )
        .count()
    )

    last_notification = (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
        )
        .order_by(
            Notification.sent_at.desc(),
            Notification.id.desc(),
        )
        .first()
    )

    return {
        "notifications_today": notifications_today,
        "notifications_this_week": notifications_this_week,
        "last_notification_at": (
            _utc(last_notification.sent_at)
            if last_notification
            else None
        ),
    }


def get_notification_context(
    db: Session,
    user_id: str,
):
    last_message = get_last_user_message(
        db=db,
        user_id=user_id,
    )

    stats = get_notification_stats(
        db=db,
        user_id=user_id,
    )

    memory = get_memory(
        user_id=user_id,
        db=db,
    )

    relationship = get_relationship(
        user_id=user_id,
        db=db,
    )

    emotion = get_emotion(
        user_id=user_id,
        db=db,
    )

    return {
        "user_id": user_id,

        "last_chat_at": (
            _utc(last_message.created_at)
            if last_message
            else None
        ),

        "last_chat_content": (
            last_message.content
            if last_message
            else None
        ),

        "notifications_today": stats[
            "notifications_today"
        ],

        "notifications_this_week": stats[
            "notifications_this_week"
        ],

        "last_notification_at": stats[
            "last_notification_at"
        ],

        "memory": memory,

        "relationship": relationship,

        "emotion": emotion,
    }
