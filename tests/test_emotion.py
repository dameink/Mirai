from core.emotion import (
    get_emotion,
    change_emotion,
    emotional_reaction
)


print("Initial:")
print(get_emotion())


change_emotion("happiness", 15)
change_emotion("stress", 30)


print("\nAfter changes:")
print(get_emotion())


print("\nReaction:")
print(emotional_reaction())

