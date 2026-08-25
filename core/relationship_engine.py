from core.relationship import change_relationship, get_relationship, load_relationship, save_relationship, clamp


RELATIONSHIP_EVENTS = {


    "gratitude": {

        "bond": 2,
        "comfort": 2,
        "affection": 1

    },


    "compliment": {

        "affection": 2,
        "comfort": 1,
        "closeness": 0.2

    },


    "achievement": {

        "respect": 3,
        "bond": 2,
        "affection": 1

    },


    "apology": {

        "trust": 2,
        "comfort": 3,
        "closeness": 1

    },

    "failure": {

        "trust":2,
        "closeness":2,
        "affection":1
    },


    "deep_conversation": {

        "closeness": 1,
        "bond": 3,
        "comfort": 3

    },


    "interest": {

        "bond": 1,
        "closeness": 0.5

    },


    "negative": {

        "comfort": -2,
        "bond": -1

    },


    "insult": {

        "bond": -5,
        "comfort": -7,
        "trust": -3

    }

}



def apply_relationship_event(event_name, intensity=1):


    if event_name not in RELATIONSHIP_EVENTS:

        print(
            f"Unknown relationship event: {event_name}"
        )

        return



    print(
        f"Applying relationship event: {event_name}"
    )


    for relationship, value in RELATIONSHIP_EVENTS[event_name].items():

        change_relationship(
            relationship,
            value * intensity
        )

def process_relationship(message):

    print("PROCESSING RELATIONSHIP")

    message = message.lower()


    # Base familiarity
    change_relationship(
        "familiarity",
        0.5
    )

    print("FAMILIARITY UPDATED")
    print(get_relationship())

    # Emotional / personal conversations create more familiarity

    deep_words = [
        "my future",
        "my dream",
        "my feelings",
        "my life",
        "i feel",
        "i am worried"
    ]


    for word in deep_words:

        if word in message:

            change_relationship(
                "familiarity",
                1.5
            )

            break
