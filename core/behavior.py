from core.emotion import get_emotion
from core.personality import personality
from core.relationship import get_relationship



def clamp(value):

    return max(0, min(100, round(value)))



def get_behavior():

    emotion = get_emotion()["state"]
    traits = personality["core_traits"]
    relationship = get_relationship()



    behavior = {


        # =========================
        # CURRENT STATE
        # =========================

        "mood": "neutral",

        "conversation_mode": "casual",



        # =========================
        # COMMUNICATION
        # =========================

        "tone": "friendly",

        "communication_style": "normal",



        # =========================
        # BEHAVIOR LEVELS
        # =========================

        "warmth": 30,

        "openness": 30,

        "playfulness": 30,

        "humor_level": 30,

        "talkativeness": 40,

        "question_frequency": 30,

        "supportiveness": 40,

        "expressiveness": 50,

        "assertiveness": 50,



        # =========================
        # INTERNAL STYLE
        # =========================

        "energy_level": "normal",

        "seriousness": 30,



        # =========================
        # RELATIONSHIP DATA
        # =========================

        "relationship_stage":
            relationship.get(
                "stage",
                "stranger"
            ),

        "closeness":
            relationship.get(
                "closeness",
                0
            ),

        "bond":
            relationship.get(
                "bond",
                0
            )

    }



    # =========================
    # EMOTION VALUES
    # =========================


    happiness = emotion.get(
        "happiness",
        50
    )

    energy = emotion.get(
        "energy",
        50
    )

    trust = emotion.get(
        "trust",
        50
    )

    curiosity = emotion.get(
        "curiosity",
        50
    )

    comfort = emotion.get(
        "comfort",
        50
    )

    stress = emotion.get(
        "stress",
        0
    )



    # =========================
    # PERSONALITY VALUES
    # =========================


    humor = traits.get(
        "humor",
        50
    )

    empathy = traits.get(
        "empathy",
        50
    )

    confidence = traits.get(
        "confidence",
        50
    )

    personality_curiosity = traits.get(
        "curiosity",
        50
    )



    # =========================
    # MOOD SYSTEM
    # =========================


    if stress >= 70:

        behavior["mood"] = "stressed"

        behavior["conversation_mode"] = "supportive"



    elif happiness >= 85:

        behavior["mood"] = "very happy"

        behavior["conversation_mode"] = "playful"



    elif happiness <= 30:

        behavior["mood"] = "sad"

        behavior["conversation_mode"] = "gentle"



    # =========================
    # ENERGY SYSTEM
    # =========================


    if energy >= 85:

        behavior["energy_level"] = "energetic"

        behavior["talkativeness"] += 20



    elif energy <= 30:

        behavior["energy_level"] = "tired"

        behavior["talkativeness"] -= 15

        behavior["seriousness"] += 20



    # =========================
    # PERSONALITY INFLUENCE
    # =========================


    behavior["humor_level"] = humor


    behavior["expressiveness"] += (
        traits.get(
            "honesty",
            50
        ) * 0.2
    )


    behavior["supportiveness"] += (
        empathy * 0.3
    )


    behavior["assertiveness"] = confidence



    behavior["question_frequency"] += (
        personality_curiosity * 0.2
    )



    # =========================
    # EMOTION INFLUENCE
    # =========================


    behavior["warmth"] += (
        trust * 0.4
    )


    behavior["openness"] += (
        trust * 0.5
    )


    behavior["question_frequency"] += (
        curiosity * 0.4
    )



    if comfort >= 70:

        behavior["supportiveness"] += 20



    if happiness >= 70:

        behavior["warmth"] += 10

        behavior["playfulness"] += 35

        behavior["talkativeness"] += 10



    # =========================
    # STRESS EFFECT
    # =========================


    if stress >= 50:

        behavior["tone"] = "calm and gentle"

        behavior["seriousness"] += 30

        behavior["supportiveness"] += 20

        behavior["humor_level"] -= 25

        behavior["playfulness"] -= 25



    if stress >= 70:

        behavior["openness"] -= 20

        behavior["conversation_mode"] = "serious"



    # =========================
    # RELATIONSHIP INFLUENCE
    # =========================


    stage = relationship.get(
        "stage",
        "stranger"
    )


    bond = relationship.get(
        "bond",
        0
    )



    if stage == "stranger":


        behavior["communication_style"] = "polite"



    elif stage == "acquaintance":


        behavior["warmth"] += 10

        behavior["openness"] += 10

        behavior["communication_style"] = "friendly"



    elif stage == "friend":


        behavior["warmth"] += 20

        behavior["openness"] += 20

        behavior["playfulness"] += 15

        behavior["communication_style"] = "personal"



    elif stage == "close friend":


        behavior["warmth"] += 30

        behavior["openness"] += 30

        behavior["playfulness"] += 25

        behavior["expressiveness"] += 15

        behavior["communication_style"] = "close"



    elif stage == "trusted friend":


        behavior["warmth"] += 40

        behavior["openness"] += 40

        behavior["expressiveness"] += 25

        behavior["communication_style"] = "very close"



    # =========================
    # BOND EFFECT
    # =========================


    if bond >= 70:


        behavior["warmth"] += 15

        behavior["supportiveness"] += 15

        behavior["expressiveness"] += 10



    # =========================
    # HIGH TRUST
    # =========================


    if trust >= 80:


        behavior["communication_style"] = (
            "warm and close"
        )

        behavior["openness"] += 10

        behavior["warmth"] += 10



    elif trust <= 30:


        behavior["communication_style"] = (
            "careful"
        )



    # =========================
    # LIMITS
    # =========================


    numeric_values = [

        "warmth",
        "openness",
        "playfulness",
        "humor_level",
        "talkativeness",
        "question_frequency",
        "supportiveness",
        "expressiveness",
        "seriousness",
        "assertiveness"

    ]


    for value in numeric_values:

        behavior[value] = clamp(
            behavior[value]
        )


    return behavior