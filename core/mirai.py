from core.analyzer import analyze_message
from core.brain import get_mirai_state
from core.decision import make_decision
from core.response_plan import create_response_plan
from core.response import generate_response
from core.social_brain import process_social_interaction


def chat(message):


    # =========================
    # 1. Understand user
    # =========================

    analysis = analyze_message(
        message
    )


    # =========================
    # 2. Social processing
    # =========================

    try:

        process_social_interaction(
            message,
            analysis
        )

    except Exception:

        pass



    # =========================
    # 3. Current Mirai state
    # =========================

    state = get_mirai_state()



    # =========================
    # 4. Decision
    # =========================

    decision = make_decision(
        message
    )



    # =========================
    # 5. Response planning
    # =========================

    plan = create_response_plan(

        cognition=analysis.get(
            "cognition"
        ),

        emotion=analysis.get(
            "emotion"
        ),

        memory=analysis.get(
            "memories"
        ),

        decision=decision

    )



    # =========================
    # 6. Generate answer
    # =========================

    response = generate_response(
        message,
        state,
        plan,
        None
    )



    # =========================
    # 7. Final output
    # =========================

    return {

        "message": message,


        "analysis": analysis,


        "decision": decision,


        "plan": plan,


        "response": response,


        "state": state

    }