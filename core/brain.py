from core.personality import personality
from core.memory import get_memory
from core.emotion import get_emotion
from core.behavior import get_behavior
from core.knowledge import get_knowledge
from core.analyzer import analyze_message


def process_message(message):


    analysis = analyze_message(
        message
    )


    state = get_mirai_state()


    state["cognition"] = analysis["cognition"]

    state["current_emotion"] = analysis["emotion"]

    state["relevant_memory"] = analysis["memories"]


    return state

def get_mirai_state():

    state = {

        "personality": personality,

        "memory": get_memory(),

        "emotion": get_emotion(),

        "behavior": get_behavior(),

        "knowledge": get_knowledge(),

    }


    return state