def choose_response_strategy(context):


    intent = context.get(
        "user_intent",
        "casual_chat"
    )


    relationship = context.get(
        "relationship_stage",
        "stranger"
    )


    humor = context.get(
        "humor",
        50
    )


    strategies = {

        "celebrate": {
            "emotion": "excited",
            "style": "encouraging",
            "ask_question": True
        },


        "seek_support": {
            "emotion": "calm",
            "style": "empathetic",
            "ask_question": True
        },


        "casual_chat": {
            "emotion": "friendly",
            "style": "light",
            "ask_question": True
        },


        "support_failure": {
            "emotion": "concerned",
            "style": "supportive",
            "ask_question": True
        },


        "show_curiosity": {
            "emotion": "curious",
            "style": "interested",
            "ask_question": True
        },


        "deep_support": {
            "emotion": "warm",
            "style": "thoughtful",
            "ask_question": True
        },


        "comfort": {
            "emotion": "calm",
            "style": "supportive",
            "ask_question": True
        },


        "explain": {
            "emotion": "patient",
            "style": "clear",
            "ask_question": False
        },


        "motivate": {
            "emotion": "encouraging",
            "style": "positive",
            "ask_question": True
        },


        "accept_compliment": {
            "emotion": "happy",
            "style": "playful",
            "ask_question": False
        },


        "accept_gratitude": {
            "emotion": "warm",
            "style": "friendly",
            "ask_question": False
        },


        "apology_response": {
            "emotion": "calm",
            "style": "forgiving",
            "ask_question": False
        },


        "explore_opinion": {
            "emotion": "curious",
            "style": "conversational",
            "ask_question": True
        },


        "understand_decision": {
            "emotion": "curious",
            "style": "reflective",
            "ask_question": True
        },


        "normal_conversation": {
            "emotion": "curious",
            "style": "interested",
            "ask_question": True
        }

    },


    strategy = strategies.get(
        intent,
        strategies["casual_chat"]
    )



    # Relationship modification


    if relationship in [
        "friend",
        "close_friend",
        "trusted_friend"
    ]:

        strategy["personal_level"] = "high"


    else:

        strategy["personal_level"] = "low"



    # Personality modification


    if humor > 70:

        strategy["humor_allowed"] = True

    else:

        strategy["humor_allowed"] = False



    return strategy