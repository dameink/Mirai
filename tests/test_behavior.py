from core.behavior import get_behavior
from core.emotion import reset_emotion, change_emotion, get_emotion


def print_behavior(title):

    print("\n====================")
    print(title)
    print("====================")

    behavior = get_behavior()

    for key, value in behavior.items():
        print(f"{key}: {value}")



# 1. Default

reset_emotion()

print_behavior("NORMAL MIRAI")



# 2. Happy

reset_emotion()
print(get_emotion())

change_emotion("happiness", 25)
change_emotion("energy", 15)

print_behavior("HAPPY MIRAI")



# 3. Stressed

reset_emotion()

change_emotion("stress", 60)
change_emotion("happiness", -40)
change_emotion("energy", -40)

print_behavior("STRESSED MIRAI")



# 4. High trust

reset_emotion()

change_emotion("trust", 50)
change_emotion("comfort", 40)

print_behavior("CLOSE MIRAI")



# 5. Curious

reset_emotion()

change_emotion("curiosity", 20)

print_behavior("CURIOUS MIRAI")