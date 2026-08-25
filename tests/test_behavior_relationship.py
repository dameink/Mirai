from core.behavior import get_behavior
from core.relationship import reset_relationship, change_relationship
from core.emotion import reset_emotion


def print_behavior(title):

    print("\n====================")
    print(title)
    print("====================")

    behavior = get_behavior()

    for key, value in behavior.items():
        print(
            key,
            ":",
            value
        )


# RESET

reset_relationship()
reset_emotion()


# Stranger

print_behavior("STRANGER")


# Simulate acquaintance

change_relationship(
    "familiarity",
    15
)

change_relationship(
    "closeness",
    20
)


print_behavior("AFTER BOND")


# Simulate close friend

change_relationship(
    "familiarity",
    70
)

change_relationship(
    "closeness",
    70
)


print_behavior("CLOSE FRIEND")