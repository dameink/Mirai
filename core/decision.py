from core.brain import process_message



def make_decision(message):


    state = process_message(
        message
    )


    decision = {


        "tone":
        state["behavior"].get(
            "tone",
            "neutral"
        ),


        "warmth":
        state["behavior"].get(
            "warmth",
            50
        ),


        "use_memory":
        False,


        "empathy":
        50,


        "humor":
        False,


        "ask_question":
        False

    }



    # ======================
    # EMOTION RULES
    # ======================


    emotion = state.get(
        "current_emotion"
    )


    if emotion:


        if emotion["emotion"] == "anxiety":


            decision["tone"] = "supportive"

            decision["empathy"] = 90

            decision["humor"] = False

            decision["ask_question"] = True



    # ======================
    # MEMORY RULES
    # ======================


    memories = state.get(
        "relevant_memory"
    )


    if memories:


        if len(
            memories.get(
                "primary",
                []
            )
        ) > 0:


            decision["use_memory"] = True



    return decision