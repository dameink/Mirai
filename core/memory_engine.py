from core.memory import (
    remember_semantic,
    remember_event,
    remember_emotion,
    update_relationship
)



MEMORY_RULES = {


    # ==========================
    # SEMANTIC MEMORY
    # Long-term facts about user
    # ==========================


    "achievement": {

        "memory_type": "semantic",

        "importance": 80,

        "category": "achievement"

    },


    "preference": {

        "memory_type": "semantic",

        "importance": 60,

        "category": "interest"

    },


    "dislike": {

        "memory_type": "semantic",

        "importance": 60,

        "category": "dislike"

    },


    "introduction": {

        "memory_type": "semantic",

        "importance": 100,

        "category": "identity"

    },


    "skill": {

        "memory_type": "semantic",

        "importance": 70,

        "category": "skill"

    },


    "goal": {

        "memory_type": "semantic",

        "importance": 90,

        "category": "goal"

    },


    "life_event": {

        "memory_type": "semantic",

        "importance": 85,

        "category": "life"

    },



    # ==========================
    # EPISODIC MEMORY
    # Specific moments
    # ==========================


    "deep_conversation": {

        "memory_type": "episodic",

        "importance": 90

    },


    "first_meeting": {

        "memory_type": "episodic",

        "importance": 100

    },


    "important_day": {

        "memory_type": "episodic",

        "importance": 90

    },


    "milestone": {

        "memory_type": "semantic",

        "importance": 85,

        "category": "project"

    },


    "shared_joke": {

        "memory_type": "episodic",

        "importance": 50

    },


    "conflict": {

        "memory_type": "episodic",

        "importance": 90

    },


    "apology": {

        "memory_type": "episodic",

        "importance": 80

    },



    # ==========================
    # EMOTIONAL MEMORY
    # Emotional patterns
    # ==========================


    "emotional_event": {

        "memory_type": "emotional",

        "importance": 80

    },


    "stress": {

        "memory_type": "emotional",

        "importance": 75

    },


    "happiness": {

        "memory_type": "emotional",

        "importance": 70

    },


    "fear": {

        "memory_type": "emotional",

        "importance": 80

    },


    "frustration": {

        "memory_type": "emotional",

        "importance": 75

    },


    "confidence_boost": {

        "memory_type": "emotional",

        "importance": 70

    },



    # ==========================
    # RELATIONSHIP MEMORY
    # Mirai + user relationship
    # ==========================


    "positive_interaction": {

        "memory_type": "relationship",

        "trust": 1,

        "affection": 2,

        "familiarity": 1

    },


    "important_interaction": {

        "memory_type": "relationship",

        "trust": 3,

        "affection": 3,

        "familiarity": 2

    },


    "support_received": {

        "memory_type": "relationship",

        "trust": 5,

        "affection": 4,

        "familiarity": 2

    },


    "personal_sharing": {

        "memory_type": "relationship",

        "trust": 7,

        "affection": 5,

        "familiarity": 3

    },


    "user_compliment": {

        "memory_type": "relationship",

        "trust": 1,

        "affection": 4,

        "familiarity": 1

    },


    "mirai_helped_user": {

        "memory_type": "relationship",

        "trust": 5,

        "affection": 3,

        "familiarity": 2

    }

}


# ==========================
# CHECK MEMORY TYPE
# ==========================


def should_remember(event):

    return event in MEMORY_RULES





# ==========================
# SAVE MEMORY
# ==========================


def save_event_memory(
        event,
        message,
        emotion=None,
        intensity=50
):


    if not should_remember(event):

        return False



    rule = MEMORY_RULES[event]


    memory_type = rule["memory_type"]



    # ----------------------
    # SEMANTIC MEMORY
    # ----------------------

    if memory_type == "semantic":


        remember_semantic(

            message,

            rule["importance"],

            rule["category"],

            emotion

        )



    # ----------------------
    # EPISODIC MEMORY
    # ----------------------

    elif memory_type == "episodic":


        remember_event(

            message,

            rule["importance"]

        )



    # ----------------------
    # EMOTIONAL MEMORY
    # ----------------------

    elif memory_type == "emotional":


        remember_emotion(

            emotion if emotion else "unknown",

            message,

            intensity

        )



    # ----------------------
    # RELATIONSHIP MEMORY
    # ----------------------

    elif memory_type == "relationship":


        update_relationship(

            trust=rule.get(
                "trust",
                0
            ),

            affection=rule.get(
                "affection",
                0
            ),

            familiarity=rule.get(
                "familiarity",
                0
            )

        )



    print(
        "Memory saved:",
        event,
        message
    )


    return True





# ==========================
# GET MEMORY IMPORTANCE
# ==========================


def get_memory_importance(event):


    if event not in MEMORY_RULES:

        return 0


    return MEMORY_RULES[event].get(
        "importance",
        0
    )





# ==========================
# ADD NEW MEMORY RULE
# ==========================


def add_memory_rule(
        name,
        memory_type,
        importance=50,
        category=None
):


    MEMORY_RULES[name] = {


        "memory_type": memory_type,


        "importance": importance,


        "category": category

    }