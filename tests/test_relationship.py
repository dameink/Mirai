from core.relationship import (
    get_relationship,
    change_relationship,
    reset_relationship
)


def show_relationship(title):

    print("\n====================")
    print(title)
    print("====================")

    relationship = get_relationship()

    for key, value in relationship.items():

        print(f"{key}: {value}")



# Reset

reset_relationship()


# Initial state

show_relationship("INITIAL RELATIONSHIP")



# First interactions

change_relationship("familiarity", 20)
change_relationship("closeness", 10)
change_relationship("bond", 5)


show_relationship("AFTER SOME INTERACTIONS")



# Becoming closer

change_relationship("familiarity", 50)
change_relationship("closeness", 50)
change_relationship("affection", 40)
change_relationship("comfort", 30)


show_relationship("CLOSE RELATIONSHIP")



# Reset test

reset_relationship()


show_relationship("AFTER RESET")