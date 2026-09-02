from core.personality import personality
from core.memory import get_memory
from core.emotion import get_emotion
from core.behavior import get_behavior
from core.knowledge import get_knowledge
from core.relationship import get_relationship
from core.learning import create_learning_context
from core.analyzer import analyze_message


def process_message(
    message,
    user_id=None,
    db=None,
):
    analysis = analyze_message(
        message,
        user_id=user_id,
        db=db,
    )

    state = get_mirai_state(
        user_id=user_id,
        db=db,
    )

    state["cognition"] = analysis.get(
        "cognition"
    )

    state["current_emotion"] = analysis.get(
        "emotion"
    )

    return state


def get_mirai_state(
    user_id=None,
    db=None,
):
    learning_context = create_learning_context(
        user_id
    )

    learning = learning_context.learning

    state = {
        "personality": personality,

        "memory": get_memory(
            user_id=user_id,
            db=db,
        ),

        "emotion": get_emotion(
            user_id=user_id,
            db=db,
        ),

        "relationship": get_relationship(
            user_id=user_id,
            db=db,
        ),

        "learning": learning.get_profile(),

        "behavior": get_behavior(),

        "knowledge": get_knowledge(),
    }

    return state