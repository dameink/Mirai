from core.personality import personality
from core.memory import get_memory
from core.emotion import get_emotion
from core.behavior import get_behavior
from core.knowledge import get_knowledge
from core.relationship import get_relationship
from core.learning import learning_context
from core.analyzer import analyze_message


def process_message(message):

    analysis = analyze_message(
        message
    )

    state = get_mirai_state()

    state["cognition"] = analysis.get(
        "cognition"
    )

    state["current_emotion"] = analysis.get(
        "emotion"
    )

    state["relevant_memory"] = analysis.get(
        "memories"
    )

    return state


def get_mirai_state():

    learning = learning_context.learning

    state = {
        "personality": personality,

        "memory": get_memory(),

        "emotion": get_emotion(),

        "relationship": get_relationship(),

        "learning": learning.get_profile(),

        "behavior": get_behavior(),

        "knowledge": get_knowledge(),
    }

    return state