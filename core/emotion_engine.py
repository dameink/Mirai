from core.emotion import change_emotion


EMOTION_EVENTS = {
    "gratitude": {
        "happiness": 3,
        "trust": 2,
        "comfort": 2,
    },

    "compliment": {
        "happiness": 5,
        "trust": 1,
        "comfort": 2,
        "excitement": 2,
    },

    "achievement": {
        "happiness": 7,
        "excitement": 5,
    },

    "interest": {
        "curiosity": 3,
        "comfort": 1,
    },

    "deep_conversation": {
        "comfort": 5,
        "trust": 3,
        "curiosity": 2,
    },

    "negative": {
        "happiness": -5,
        "trust": -4,
        "comfort": -5,
        "stress": 5,
    },

    "apology": {
        "happiness": 3,
        "trust": 4,
        "comfort": 5,
        "stress": -3,
    },
}


def apply_emotion_event(
    event_name,
    intensity=1,
    user_id=None,
    db=None,
):
    if event_name not in EMOTION_EVENTS:
        print(
            f"Unknown emotion event: {event_name}"
        )
        return

    event = EMOTION_EVENTS[event_name]

    print(
        f"Applying emotion event: {event_name}"
    )

    for emotion_name, value in event.items():

        change_emotion(
            emotion_name,
            value * intensity,
            user_id=user_id,
            db=db,
        )