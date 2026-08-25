from core.emotion_engine import process_emotion
from core.emotion import get_emotion


print("START")

print(get_emotion())


print("\n--- SOCIAL BRAIN EVENT ---")


process_emotion(
    "random message",
    forced_event="achievement"
)


print(get_emotion())