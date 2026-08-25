from core.emotion import get_emotion, change_emotion, decay_emotions


change_emotion("happiness", 20)
change_emotion("stress", 30)


print("Before decay:")
print(get_emotion())


decay_emotions()


print("\nAfter decay:")
print(get_emotion())