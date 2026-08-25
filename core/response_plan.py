from typing import Dict


def create_response_plan(
        cognition,
        emotion,
        memory,
        decision
):

    plan = {

        "main_goal": "answer_user",

        "steps": [],

        "avoid": []

    }


    # =========================
    # EMOTIONAL RESPONSE
    # =========================

    if emotion:

        if emotion.get("emotion") == "anxiety":

            plan["main_goal"] = "support_user"

            plan["steps"].extend([
                "acknowledge user's feelings",
                "show empathy",
                "provide encouragement"
            ])

            plan["avoid"].append(
                "do not use humor"
            )


        elif emotion.get("emotion") == "happiness":

            plan["main_goal"] = "share_positive_emotion"

            plan["steps"].extend([
                "celebrate user's emotion",
                "show excitement"
            ])


    # =========================
    # MEMORY USAGE
    # =========================

    if decision.get(
        "use_memory",
        False
    ):

        plan["steps"].append(
            "use relevant memory naturally"
        )


    # =========================
    # QUESTIONS
    # =========================

    if decision.get(
        "ask_question",
        False
    ):

        plan["steps"].append(
            "ask a meaningful follow-up question"
        )


    # =========================
    # TONE
    # =========================

    plan["tone"] = decision.get(
        "tone",
        "friendly"
    )


    plan["warmth"] = decision.get(
        "warmth",
        50
    )


    plan["empathy"] = decision.get(
        "empathy",
        50
    )


    return plan