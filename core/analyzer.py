from core.cognition import understand_message
from core.memory_recall import recall_memory
from core.emotion import analyze_emotion



def analyze_message(message):


    cognition = understand_message(
        message
    )


    emotion = analyze_emotion(
        message
    )


    memories = recall_memory(
        message,
        cognition=cognition
    )


    return {

        "message":message,

        "cognition":cognition,

        "emotion":emotion,

        "memories":memories

    }