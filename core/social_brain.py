from core.event_detector import (
    detect_event,
    calculate_event_intensity
)
from core.emotion_engine import apply_emotion_event
from core.relationship_engine import (
    apply_relationship_event,
    process_relationship
)
from core.emotion import get_emotion
from core.relationship import get_relationship
from core.behavior import get_behavior
from core.memory_engine import save_event_memory



def process_social_interaction(message):


    event_data = detect_event(message)
    event = event_data["event"]
    intensity = calculate_event_intensity(message)


    print(
        "Detected event:",
        event
    )


    # Relationship updates happen EVERY conversation
    process_relationship(message)


    if event != "neutral":

        save_event_memory(
            event,
            message
        )


        apply_emotion_event(
            event,
            intensity
        )


        apply_relationship_event(
            event,
            intensity
        )


    return {

        "event": event,

        "emotion": get_emotion(),

        "relationship": get_relationship(),

        "behavior": get_behavior()

    }
