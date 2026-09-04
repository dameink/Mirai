import random
from datetime import datetime, timezone
from typing import Optional

from notifications.templates import TEMPLATES
from db.models import Notification, PushToken
from notifications.push import send_push_notification

# Priority: higher number = more important
NOTIFICATION_PRIORITY = {
    "follow_up": 100,
    "conversation": 80,
    "curiosity": 70,
    "miss_you": 60,
    "emotion": 50,
    "learning": 30,
}


def hours_since(dt: Optional[datetime]) -> Optional[float]:
    """Return hours passed since a datetime."""
    if dt is None:
        return None

    now = datetime.now(timezone.utc)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return (now - dt).total_seconds() / 3600


def can_notify(
    last_notification_at: Optional[datetime],
    notifications_today: int,
    notifications_this_week: int,
    last_chat_at: Optional[datetime],
) -> bool:
    """
    Check global notification limits.
    """

    # Maximum one notification per day
    if notifications_today >= 1:
        return False

    # Maximum three notifications per week
    if notifications_this_week >= 3:
        return False

    # Do not notify shortly after a conversation
    chat_hours = hours_since(last_chat_at)

    if chat_hours is not None and chat_hours < 8:
        return False

    # Minimum time between notifications
    notification_hours = hours_since(last_notification_at)

    if notification_hours is not None and notification_hours < 8:
        return False

    return True


def choose_notification_type(
    available_types: list[str],
) -> Optional[str]:
    """
    Select the highest-priority available notification type.
    """

    if not available_types:
        return None

    return max(
        available_types,
        key=lambda notification_type: NOTIFICATION_PRIORITY.get(
            notification_type,
            0,
        ),
    )


def choose_message(
    notification_type: str,
    emotion: Optional[str] = None,
) -> Optional[str]:
    """
    Choose a message from the template pool.
    """

    if notification_type == "emotion":
        emotion_templates = TEMPLATES.get("emotion", {})

        if emotion in emotion_templates:
            return random.choice(emotion_templates[emotion])

        if "low" in emotion_templates:
            return random.choice(emotion_templates["low"])

        return None

    templates = TEMPLATES.get(notification_type)

    if not templates:
        return None

    return random.choice(templates)


def generate_notification(
    available_types: list[str],
    emotion: Optional[str] = None,
):
    """
    Generate a notification from the currently available types.
    """

    notification_type = choose_notification_type(
        available_types
    )

    if notification_type is None:
        return None

    message = choose_message(
        notification_type=notification_type,
        emotion=emotion,
    )

    if message is None:
        return None

    return {
        "type": notification_type,
        "title": "Mirai 🌸",
        "body": message,
        "data": {
            "type": notification_type,
        },
    }

def send_notification(
    db,
    user_id: str,
    notification: dict,
):
    """
    Send a notification to the user's registered push token
    and save it to the notification history.
    """

    push_token = (
        db.query(PushToken)
        .filter(PushToken.user_id == user_id)
        .first()
    )

    if not push_token:
        return {
            "success": False,
            "message": "No push token registered",
        }

    result = send_push_notification(
        token=push_token.token,
        title=notification["title"],
        body=notification["body"],
        data=notification.get("data", {}),
    )

    if not result.get("success"):
        return result

    history = Notification(
        user_id=user_id,
        type=notification["type"],
        title=notification["title"],
        body=notification["body"],
    )

    db.add(history)
    db.commit()
    db.refresh(history)

    return {
        "success": True,
        "notification_id": history.id,
        "type": history.type,
        "body": history.body,
    }