from core.cognition import understand_message
from core.emotion import analyze_emotion


def analyze_message(message, user_id=None, db=None):
    cognition = understand_message(message)

    emotion = analyze_emotion(message)

    return {
        "message": message,
        "cognition": cognition,
        "emotion": emotion,
    }