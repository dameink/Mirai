from core.event_detector import detect_event



messages = [

    "Thank you Mirai, you helped me",

    "You are amazing",

    "I passed my physics exam",

    "Sorry Mirai, my bad",

    "You are useless",

    "I want to talk about my future",

    "Hello Mirai"

]


for message in messages:

    print("\n====================")

    print(message)

    print(
        detect_event(message)
    )