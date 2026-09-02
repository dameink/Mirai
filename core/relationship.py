import json
import os

from core.user_state import get_user_file


RELATIONSHIP_FILE = "relationship.json"


DEFAULT_RELATIONSHIP = {
    "familiarity": 0,
    "bond": 20,
    "closeness": 0,
    "affection": 0,
    "respect": 50,
    "comfort": 50,
    "stage": "stranger",
}


def _relationship_file(user_id=None):
    if user_id:
        return get_user_file(
            user_id,
            RELATIONSHIP_FILE,
        )

    return RELATIONSHIP_FILE


def load_relationship(user_id=None):
    relationship_file = _relationship_file(user_id)

    if not os.path.exists(relationship_file):
        save_relationship(
            DEFAULT_RELATIONSHIP,
            user_id=user_id,
        )

        return DEFAULT_RELATIONSHIP.copy()

    try:
        with open(
            relationship_file,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        for key, value in DEFAULT_RELATIONSHIP.items():
            if key not in data:
                data[key] = value

        return data

    except json.JSONDecodeError:
        save_relationship(
            DEFAULT_RELATIONSHIP,
            user_id=user_id,
        )

        return DEFAULT_RELATIONSHIP.copy()


def save_relationship(
    relationship,
    user_id=None,
):
    relationship_file = _relationship_file(user_id)

    os.makedirs(
        os.path.dirname(relationship_file) or ".",
        exist_ok=True,
    )

    with open(
        relationship_file,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            relationship,
            file,
            indent=4,
            ensure_ascii=False,
        )


def clamp(value):
    return max(
        0,
        min(
            100,
            round(value, 2),
        ),
    )


def change_relationship(
    parameter,
    amount,
    user_id=None,
    db=None,
):
    relationship = load_relationship(
        user_id=user_id
    )

    if parameter in relationship:

        # Only numeric relationship parameters
        # can be changed.
        if isinstance(
            relationship[parameter],
            (int, float),
        ):
            relationship[parameter] += amount

            relationship[parameter] = clamp(
                relationship[parameter]
            )

    update_relationship_stage(
        relationship
    )

    save_relationship(
        relationship,
        user_id=user_id,
    )


def update_relationship_stage(
    relationship
):
    familiarity = relationship["familiarity"]
    bond = relationship["bond"]
    closeness = relationship["closeness"]

    score = (
        familiarity * 0.3
        + bond * 0.3
        + closeness * 0.4
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


def get_relationship(user_id=None, db=None):
    relationship = load_relationship(
        user_id=user_id
    )

    update_relationship_stage(relationship)

    save_relationship(
        relationship,
        user_id=user_id,
    )

    return relationship


def reset_relationship(user_id=None):
    save_relationship(
        DEFAULT_RELATIONSHIP,
        user_id=user_id,
    )