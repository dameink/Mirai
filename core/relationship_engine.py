from core.relationship import change_relationship


RELATIONSHIP_EVENTS = {
    "gratitude": {
        "bond": 2,
        "comfort": 2,
        "affection": 1,
    },

    "compliment": {
        "affection": 2,
        "comfort": 1,
        "closeness": 0.2,
    },

    "achievement": {
        "respect": 3,
        "bond": 2,
        "affection": 1,
    },

    "apology": {
        "trust": 2,
        "comfort": 3,
        "closeness": 1,
    },

    "failure": {
        "trust": 2,
        "closeness": 2,
        "affection": 1,
    },

    "deep_conversation": {
        "closeness": 1,
        "bond": 3,
        "comfort": 3,
    },

    "interest": {
        "bond": 1,
        "closeness": 0.5,
    },

    "negative": {
        "comfort": -2,
        "bond": -1,
    },

    "insult": {
        "bond": -5,
        "comfort": -7,
        "trust": -3,
    },
}


DEEP_WORDS = [
    "my future",
    "my dream",
    "my feelings",
    "my life",
    "i feel",
    "i am worried",
]


def apply_relationship_event(
    event_name,
    intensity=1,
    user_id=None,
    message=None,
    db=None,
):
    """
    Apply all relationship changes for one interaction.

    This is the single authoritative relationship mutation point.
    """

    print(
        f"Applying relationship event: {event_name}"
    )

    # ========================================
    # BASE FAMILIARITY
    # ========================================

    change_relationship(
        "familiarity",
        0.5,
        user_id=user_id,
    )

    # ========================================
    # DEEP CONVERSATION
    # ========================================

    if message:
        message_lower = message.lower()

        for word in DEEP_WORDS:
            if word in message_lower:
                change_relationship(
                    "familiarity",
                    1.5,
                    user_id=user_id,
                )
                break

    # ========================================
    # EVENT RELATIONSHIP CHANGES
    # ========================================

    if event_name not in RELATIONSHIP_EVENTS:
        print(
            f"Unknown relationship event: {event_name}"
        )
        return

    for parameter, value in RELATIONSHIP_EVENTS[
        event_name
    ].items():

        change_relationship(
            parameter,
            value * intensity,
            user_id=user_id,
        )