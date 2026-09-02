from core.brain import get_mirai_state


def make_decision(
    message,
    analysis,
    user_id=None,
    db=None,
):
    """
    Decide how Mirai should respond based on
    already calculated analysis and current state.
    """

    state = get_mirai_state(
        user_id=user_id,
        db=db,
    )

    decision = {
        "tone": state["behavior"].get(
            "tone",
            "neutral"
        ),

        "warmth": state["behavior"].get(
            "warmth",
            50
        ),

        "use_memory": False,

        "empathy": 50,

        "humor": False,

        "ask_question": False
    }

    # =========================
    # EMOTION RULES
    # =========================

    emotion = analysis.get(
        "emotion"
    )

    if emotion:

        emotion_type = emotion.get(
            "emotion"
        )

        if emotion_type == "anxiety":

            decision["tone"] = "supportive"
            decision["empathy"] = 90
            decision["humor"] = False
            decision["ask_question"] = True

        elif emotion_type == "happiness":

            decision["tone"] = "positive"
            decision["empathy"] = 70
            decision["humor"] = True

        elif emotion_type == "sadness":

            decision["tone"] = "supportive"
            decision["empathy"] = 85
            decision["humor"] = False

    # =========================
    # MEMORY RULES
    # =========================

    memories = analysis.get(
        "memories"
    )

    if memories:

        primary = memories.get(
            "primary",
            []
        )

        if primary:

            decision["use_memory"] = True

    # =========================
    # RECALL INTENT
    # =========================

    cognition = analysis.get(
        "cognition",
        {}
    )

    if cognition.get(
        "intent"
    ) == "recall":

        decision["use_memory"] = True

    # =========================
    # GENERAL CONVERSATION
    # =========================

    if cognition.get(
        "intent"
    ) == "conversation":

        if decision["tone"] == "neutral":
            decision["tone"] = "friendly"

    return decision