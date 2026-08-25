from core.relationship import get_relationship, reset_relationship
from core.relationship_engine import process_relationship


def show(title):

    print("\n====================")
    print(title)
    print("====================")

    for key, value in get_relationship().items():
        print(f"{key}: {value}")


reset_relationship()


show("START")


process_relationship(
    "Thank you Mirai, you helped me"
)

show("HELP")


process_relationship(
    "I feel worried about my future"
)

show("DEEP TALK")


process_relationship(
    "Sorry Mirai, my bad"
)

show("APOLOGY")


process_relationship(
    "You are my best friend"
)

show("FINAL")