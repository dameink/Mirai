from core.memory_recall import recall_memory
from core.emotion import get_emotion


def analyze_message(message):

    result = {

        "message": message,

        "memories": recall_memory(message),

        "emotion": get_emotion()

    }

    return result



test = analyze_message(
    "I am nervous about my university interview"
)


print(test)