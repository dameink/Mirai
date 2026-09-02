from core.memory import get_memory
from core.user_state import get_user_file

from datetime import datetime
import json
import os


# =====================================
# PROFILE STORAGE
# =====================================

LEGACY_PROFILE_FILE = "memory/profile.json"


def _profile_file(user_id=None):
    if user_id:
        return get_user_file(
            user_id,
            "profile.json"
        )

    return LEGACY_PROFILE_FILE


def load_profile(user_id=None):

    profile_file = _profile_file(user_id)

    if not os.path.exists(profile_file):

        return {
            "identity": {},
            "interests": [],
            "goals": [],
            "traits": [],
            "learning_style": {},
            "communication_style": {},
            "updated": None
        }

    with open(
        profile_file,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def save_profile(
    profile,
    user_id=None
):

    profile_file = _profile_file(user_id)

    directory = os.path.dirname(
        profile_file
    )

    if directory:
        os.makedirs(
            directory,
            exist_ok=True
        )

    profile["updated"] = (
        datetime.now()
        .isoformat()
    )

    with open(
        profile_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            profile,
            f,
            indent=4,
            ensure_ascii=False
        )


# =====================================
# ADD OR UPDATE ITEM
# =====================================

def update_score(
    collection,
    name,
    evidence,
    amount=10
):

    for item in collection:

        if item["name"] == name:

            item["confidence"] += amount

            item["confidence"] = min(
                100,
                item["confidence"]
            )

            item["evidence"].append(
                evidence
            )

            return

    collection.append({

        "name": name,

        "confidence": 50,

        "evidence": [
            evidence
        ]

    })


# =====================================
# INTEREST ANALYSIS
# =====================================

def analyze_interests(
    memories,
    profile
):

    facts = memories[
        "semantic"
    ][
        "facts"
    ]

    for fact in facts:

        category = fact.get(
            "category"
        )

        content = fact.get(
            "content",
            ""
        ).lower()

        if category == "interest":

            update_score(

                profile["interests"],

                content.replace(
                    "user likes ",
                    ""
                ),

                content

            )


# =====================================
# GOAL ANALYSIS
# =====================================

def analyze_goals(
    memories,
    profile
):

    facts = memories[
        "semantic"
    ][
        "facts"
    ]

    for fact in facts:

        if fact.get(
            "category"
        ) == "goal":

            update_score(

                profile["goals"],

                fact["content"],

                fact["content"],

                amount=15

            )


# =====================================
# PERSONALITY INFERENCE
# =====================================

def analyze_traits(
    memories,
    profile
):

    all_text = ""

    for item in memories[
        "semantic"
    ][
        "facts"
    ]:

        all_text += (
            item["content"]
            .lower()
            + " "
        )

    for item in memories[
        "episodic"
    ][
        "events"
    ]:

        all_text += (
            item["content"]
            .lower()
            + " "
        )

    rules = {

        "ambitious": [
            "goal",
            "want to become",
            "building",
            "project"
        ],

        "curious": [
            "learn",
            "physics",
            "science",
            "research"
        ],

        "persistent": [
            "finished",
            "passed",
            "completed"
        ],

        "creative": [
            "create",
            "building",
            "application"
        ]

    }

    for trait, keywords in rules.items():

        score = 0

        evidence = []

        for word in keywords:

            if word in all_text:

                score += 20

                evidence.append(
                    word
                )

        if score > 0:

            update_score(

                profile["traits"],

                trait,

                evidence,

                score

            )


# =====================================
# LEARNING STYLE
# =====================================

def analyze_learning_style(
    memories,
    profile
):

    events = memories[
        "episodic"
    ][
        "events"
    ]

    for event in events:

        text = event[
            "content"
        ].lower()

        if (
            "study" in text
            or
            "learn" in text
        ):

            profile[
                "learning_style"
            ][
                "active_learning"
            ] = True


# =====================================
# COMMUNICATION STYLE
# =====================================

def analyze_communication(
    memories,
    profile
):

    profile[
        "communication_style"
    ] = {

        "prefers_detailed_answers": True,

        "likes_deep_discussion": True

    }


# =====================================
# MAIN PROFILE UPDATE
# =====================================

def update_profile(user_id=None):

    memories = get_memory(
        user_id=user_id
    )

    profile = load_profile(
        user_id=user_id
    )

    analyze_interests(
        memories,
        profile
    )

    analyze_goals(
        memories,
        profile
    )

    analyze_traits(
        memories,
        profile
    )

    analyze_learning_style(
        memories,
        profile
    )

    analyze_communication(
        memories,
        profile
    )

    save_profile(
        profile,
        user_id=user_id
    )

    return profile