from core.emotion_engine import process_emotion
from core.emotion import reset_emotion, get_emotion


reset_emotion()


print("START")
print(get_emotion())


print("\n--- GRATITUDE ---")

process_emotion(
    "Thank you Mirai"
)

print(get_emotion())


print("\n--- COMPLIMENT ---")

process_emotion(
    "You are amazing"
)

print(get_emotion())


print("\n--- NEGATIVE ---")

process_emotion(
    "You are useless"
)

print(get_emotion())