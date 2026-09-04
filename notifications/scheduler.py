from notifications.notifications import (
    can_notify,
    generate_notification,
)
from notifications.context import get_notification_context


def get_available_notification_types(context):
    """
    Determine which notification types are appropriate
    for the current user context.
    """

    available = []

    relationship = context.get("relationship", {})
    emotion = context.get("emotion", {})
    memory = context.get("memory", {})

    stage = relationship.get("stage", "stranger")

    emotion_state = emotion.get("state", {})

    stress = emotion_state.get("stress", 20)
    energy = emotion_state.get("energy", 80)
    curiosity = emotion_state.get("curiosity", 80)

    # --------------------------------------------------
    # 1. Follow-up
    # --------------------------------------------------

    episodic_events = memory.get(
        "episodic",
        {},
    ).get(
        "events",
        [],
    )

    important_events = [
        event
        for event in episodic_events
        if event.get("importance", 0) >= 70
    ]

    if important_events:
        available.append("follow_up")

    # --------------------------------------------------
    # 2. Conversation
    # --------------------------------------------------

    if stage in {
        "acquaintance",
        "friend",
        "close_friend",
        "trusted_friend",
    }:
        available.append("conversation")

    # --------------------------------------------------
    # 3. Curiosity
    # --------------------------------------------------

    if curiosity >= 70 and stage in {
        "friend",
        "close_friend",
        "trusted_friend",
    }:
        available.append("curiosity")

    # --------------------------------------------------
    # 4. Miss you
    # --------------------------------------------------

    if stage in {
        "friend",
        "close_friend",
        "trusted_friend",
    }:
        available.append("miss_you")

    # --------------------------------------------------
    # 5. Emotion
    # --------------------------------------------------

    if stress < 70 and energy >= 30:
        if emotion_state.get("happiness", 0) >= 80:
            available.append("emotion")

        elif emotion_state.get("excitement", 0) >= 75:
            available.append("emotion")

        elif emotion_state.get("happiness", 0) <= 50:
            available.append("emotion")

    # --------------------------------------------------
    # 6. Learning
    # --------------------------------------------------

    if stage in {
        "friend",
        "close_friend",
        "trusted_friend",
    }:
        available.append("learning")

    return available


def check_user_notifications(
    last_notification_at=None,
    notifications_today=0,
    notifications_this_week=0,
    last_chat_at=None,
    available_types=None,
    emotion=None,
):
    """
    Legacy checker.

    Kept for compatibility with existing tests.
    """

    if available_types is None:
        available_types = []

    allowed = can_notify(
        last_notification_at=last_notification_at,
        notifications_today=notifications_today,
        notifications_this_week=notifications_this_week,
        last_chat_at=last_chat_at,
    )

    if not allowed:
        return None

    return generate_notification(
        available_types=available_types,
        emotion=emotion,
    )


def check_user_notifications_for_user(
    db,
    user_id: str,
):
    from db.models import User

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user or not user.notifications_enabled:
        return None
    """
    Build the user's real notification context,
    determine appropriate notification types,
    and generate a notification if allowed.
    """

    context = get_notification_context(
        db=db,
        user_id=user_id,
    )

    allowed = can_notify(
        last_notification_at=context[
            "last_notification_at"
        ],
        notifications_today=context[
            "notifications_today"
        ],
        notifications_this_week=context[
            "notifications_this_week"
        ],
        last_chat_at=context[
            "last_chat_at"
        ],
    )

    if not allowed:
        return None

    available_types = get_available_notification_types(
        context
    )

    if not available_types:
        return None

    emotion_state = context.get(
        "emotion",
        {},
    ).get(
        "state",
        {},
    )

    emotion = None

    if emotion_state.get("happiness", 0) >= 80:
        emotion = "happy"

    elif emotion_state.get("excitement", 0) >= 75:
        emotion = "excited"

    elif emotion_state.get("happiness", 0) <= 50:
        emotion = "low"

    return generate_notification(
        available_types=available_types,
        emotion=emotion,
    )
