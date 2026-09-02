from core.event_detector import (
    detect_event,
    calculate_event_intensity,
)

from core.emotion_engine import apply_emotion_event

from core.relationship_engine import apply_relationship_event

from core.emotion import get_emotion
from core.relationship import get_relationship
from core.behavior import get_behavior

from core.memory_engine import save_event_memory


def process_social_interaction(
    message,
    user_id=None,
    db=None,
):
    """
    Process one social interaction.

    This is the single authoritative pipeline for:
    - event detection
    - memory storage
    - emotion mutation
    - relationship mutation
    """

    event_data = detect_event(message)

    event = event_data["event"]

    intensity = calculate_event_intensity(message)

    print(
        "Detected event:",
        event,
    )

    # ========================================
    # MEMORY
    # ========================================

    if event != "neutral":
        save_event_memory(
            event,
            message,
            user_id=user_id,
            db=db,
        )

    # ========================================
    # EMOTION
    #
    # Exactly one emotion mutation.
    # ========================================

    if event != "neutral":
        apply_emotion_event(
            event,
            intensity,
            user_id=user_id,
            db=db,
        )

    # ========================================
    # RELATIONSHIP
    #
    # Exactly one relationship mutation.
    # ========================================

    apply_relationship_event(
        event,
        intensity,
        user_id=user_id,
        message=message,
        db=db,
    )

    # ========================================
    # CURRENT USER STATE
    # ========================================

    return {
        "event": event,

        "emotion": get_emotion(
            user_id=user_id,
            db=db,
        ),

        "relationship": get_relationship(
            user_id=user_id,
            db=db,
        ),

        "behavior": get_behavior(),
    }