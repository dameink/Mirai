from core.brain import get_mirai_state
from core.analyzer import analyze_message
from core.decision import make_decision
from core.response_plan import create_response_plan



# =====================================
# MIRAI BRAIN
# Main thinking system
# =====================================


def think(message, user_id=None):


    # ===============================
    # 1. ANALYZE USER MESSAGE
    # ===============================

    analysis = analyze_message(
        message, user_id=user_id
    )


    # ===============================
    # 2. GET MIRAI INTERNAL STATE
    # ===============================

    state = get_mirai_state(user_id=user_id)



    # ===============================
    # 3. MAKE DECISION
    # ===============================

    decision = make_decision(
        message, analysis, user_id=user_id
    )



    # ===============================
    # 4. CREATE RESPONSE PLAN
    # ===============================

    response_plan = create_response_plan(
        cognition=analysis.get(
            "cognition",
            {}
        ),

        emotion=analysis.get(
            "emotion"
        ),

        memory=analysis.get(
            "memories",
            {}
        ),

        decision=decision
    )



    # ===============================
    # 5. BUILD BRAIN OUTPUT
    # ===============================

    brain_state = {


        "input": {

            "message": message

        },


        "cognition": {

            "context":
            analysis.get(
                "cognition",
                {}
            ).get(
                "context"
            ),


            "intent":
            analysis.get(
                "cognition",
                {}
            ).get(
                "intent"
            ),


            "importance":
            analysis.get(
                "cognition",
                {}
            ).get(
                "importance"
            )

        },


        "user_emotion":
        analysis.get(
            "emotion"
        ),



        "memory": {

            "relevant":
            analysis.get(
                "memories",
                {}
            ),


            "available":
            True

        },



        "mirai_state": {

            "personality":
            state.get(
                "personality"
            ),


            "emotion":
            state.get(
                "emotion"
            ),


            "behavior":
            state.get(
                "behavior"
            ),


            "knowledge":
            state.get(
                "knowledge"
            )

        },


        "decision":
        decision,


        "response_plan":
        response_plan

    }



    return brain_state