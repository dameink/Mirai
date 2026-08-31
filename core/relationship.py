import json
import os


RELATIONSHIP_FILE = "relationship.json"


DEFAULT_RELATIONSHIP = {

    "familiarity": 0,
    "bond": 20,
    "closeness": 0,
    "affection": 0,
    "respect": 50,
    "comfort": 50,
    "stage": "stranger"

}



def load_relationship():

    if not os.path.exists(RELATIONSHIP_FILE):

        save_relationship(DEFAULT_RELATIONSHIP)

        return DEFAULT_RELATIONSHIP


    try:

        with open(RELATIONSHIP_FILE, "r") as file:

            data = json.load(file)


        for key, value in DEFAULT_RELATIONSHIP.items():

            if key not in data:

                data[key] = value


        return data


    except json.JSONDecodeError:

        save_relationship(DEFAULT_RELATIONSHIP)

        return DEFAULT_RELATIONSHIP



def save_relationship(relationship):

    with open(RELATIONSHIP_FILE, "w") as file:

        json.dump(
            relationship,
            file,
            indent=4
        )



def clamp(value):

    return max(
        0,
        min(
            100,
            round(value, 2)
        )
    )

def change_relationship(parameter, amount):

    relationship = load_relationship()


    if parameter in relationship:

        relationship[parameter] += amount

        relationship[parameter] = clamp(
            relationship[parameter]
        )


    update_relationship_stage(relationship)


    save_relationship(relationship)



def update_relationship_stage(relationship):


    familiarity = relationship["familiarity"]
    bond = relationship["bond"]
    closeness = relationship["closeness"]


    score = (
        familiarity * 0.3
        +
        bond * 0.3
        +
        closeness * 0.4
    )


    if score < 20:

        relationship["stage"] = "stranger"


    elif score < 40:

        relationship["stage"] = "acquaintance"


    elif score < 60:

        relationship["stage"] = "friend"


    elif score < 80:

        relationship["stage"] = "close_friend"


    else:

        relationship["stage"] = "trusted_friend"




def get_relationship():

    relationship = load_relationship()

    update_relationship_stage(
        relationship
    )

    save_relationship(relationship)

    return relationship



def reset_relationship():

    save_relationship(DEFAULT_RELATIONSHIP)