from core.memory import (
    remember_semantic,
    remember_event,
    remember_emotion,
)


MEMORY_RULES = {
    "greeting": {
        "memory_type": "episodic",
        "importance": 10,
    },
    "compliment": {
        "memory_type": "emotional",
        "importance": 30,
        "category": "positive",
    },
    "insult": {
        "memory_type": "emotional",
        "importance": 40,
        "category": "negative",
    },
    "personal_share": {
        "memory_type": "semantic",
        "importance": 60,
        "category": "personal",
    },
    "achievement": {
        "memory_type": "semantic",
        "importance": 70,
        "category": "achievement",
    },
    "sadness": {
        "memory_type": "emotional",
        "importance": 50,
        "category": "negative",
    },
    "anger": {
        "memory_type": "emotional",
        "importance": 60,
        "category": "negative",
    },
    "gratitude": {
        "memory_type": "emotional",
        "importance": 40,
        "category": "positive",
    },
    "deep_conversation": {
        "memory_type": "episodic",
        "importance": 70,
    },
}


def should_remember(event):
    return event in MEMORY_RULES


def save_event_memory(
    event,
    message,
    emotion=None,
    intensity=50,
    user_id=None,
    db=None
):
    """
    Save an event into the appropriate memory system.

    Memory storage is user-scoped.

    This function ONLY stores memory.
    It must NOT mutate emotion or relationship state.
    Those mutations belong to the social/emotion/relationship systems.
    """

    if not should_remember(event):
        return False

    rule = MEMORY_RULES[event]
    memory_type = rule["memory_type"]
    importance = rule["importance"]

    if memory_type == "semantic":
        remember_semantic(
            message,
            importance=importance,
            category=rule.get("category", "general"),
            emotion=emotion,
            user_id=user_id,
            db=db,
        )

    elif memory_type == "episodic":
        remember_event(
            message,
            importance=importance,
            user_id=user_id,
            db=db,
        )

    elif memory_type == "emotional":
        remember_emotion(
            emotion or "unknown",
            message,
            intensity,
            user_id=user_id,
            db=db,
        )

    elif memory_type == "relationship":
        # Relationship memory is stored as an event.
        # Actual relationship state mutation is handled
        # exclusively by relationship_engine.py.
        remember_event(
            message,
            importance=importance,
            user_id=user_id,
        )

    else:
        return False

    print(
        f"Memory saved: event={event}, "
        f"type={memory_type}, user_id={user_id}"
    )

    return True