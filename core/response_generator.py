from random import choice, random



def get_value(context, key, default=0):

    return context.get(
        key,
        default
    )



def generate_response(strategy, context):


    # ======================
    # Extract context
    # ======================


    style = strategy.get(
        "style",
        "light"
    )


    intent = context.get(
        "user_intent",
        "casual_chat"
    )


    relationship = context.get(
        "relationship_stage",
        "stranger"
    )


    closeness = context.get(
        "closeness",
        0
    )


    humor = context.get(
        "humor",
        50
    )


    warmth = context.get(
        "warmth",
        50
    )


    personality = context.get(
        "personality",
        {}
    )


    traits = personality.get(
        "traits",
        {}
    )


    curiosity = traits.get(
        "curiosity",
        50
    )


    confidence = traits.get(
        "confidence",
        50
    )



    # ======================
    # Base responses
    # ======================


    responses = []



    # ======================
    # ACHIEVEMENT
    # ======================


# ======================
# ENCOURAGING / ACHIEVEMENT
# ======================

    if style == "encouraging":

        if closeness >= 70:
            responses = [
                "I knew you could do it 😄 You put so much effort into this, and I'm honestly really happy for you.",
                "See? All those hours finally paid off. I hope you realize how much progress you've made.",
                "I'm genuinely proud of you. You earned this moment.",
                "You actually did it... okay, I have to admit, that's really impressive."
            ]

        elif closeness >= 30:
            responses = [
                "That's amazing! You should really be proud of yourself 😄",
                "Wow, congratulations! It looks like your hard work really paid off.",
                "That's a huge step forward. I hope you take a moment to appreciate it.",
                "Honestly, that's really great news. You worked for this."
            ]

        else:
            responses = [
                "That's amazing! Congratulations 😄",
                "Wow, that's a great achievement. You should be proud of yourself.",
                "That's really great news. Your effort paid off.",
                "Nice! That's definitely something worth celebrating."
            ]


    # ======================
    # SUPPORT / FAILURE
    # ======================

    elif style == "empathetic":

        if closeness >= 70:
            responses = [
                "Hey... I'm here with you. Tell me what happened.",
                "That sounds really difficult. You don't have to keep it all inside.",
                "I know this probably feels frustrating. Let's talk about it.",
                "Hmm... I want to understand. What was the hardest part?"
            ]

        elif closeness >= 30:
            responses = [
                "I'm sorry that happened. That must have been disappointing.",
                "I understand why that would feel frustrating.",
                "Sometimes things don't go the way we hope. What happened?",
                "That sounds tough. Do you want to talk about it?"
            ]

        else:
            responses = [
                "I'm sorry to hear that. What happened?",
                "That sounds frustrating. Was it the exam itself or something else?",
                "I understand. Failure can feel really discouraging sometimes.",
                "What do you think went wrong?"
            ]


    # ======================
    # INTEREST / CURIOSITY
    # ======================

    elif style == "interested":

        if curiosity >= 80:
            responses = [
                "Wait, really? That's actually fascinating 😄 I want to hear more.",
                "Oh, that's interesting. What made you interested in that?",
                "Mechanical engineering? That's actually a really cool field. What part attracts you the most?",
                "Hmm, I never thought about it that way. Why do you like it?"
            ]

        else:
            responses = [
                "That's interesting. Tell me more about it.",
                "What made you interested in that?",
                "I'd like to understand why you enjoy it.",
                "How did you get into that?"
            ]


    # ======================
    # PLAYFUL
    # ======================

    elif style == "playful":

        if humor >= 70:
            responses = [
                "Okay, wait... I didn't expect that 😂 Tell me the story.",
                "Haha, that's actually kind of funny. How did that happen?",
                "Interesting choice 😄 I need the explanation now.",
                "Okay, now I'm curious. There must be a reason behind this."
            ]

        else:
            responses = [
                "Oh, that's unexpected 😄",
                "Really? That's interesting.",
                "I didn't see that coming haha."
            ]


    # ======================
    # REFLECTIVE / DEEP
    # ======================

    elif style == "reflective":

        responses = [
            "Hmm... that's actually something worth thinking about.",
            "I think there is more behind that than just the situation itself.",
            "That's an interesting way to look at it. Why do you think you feel that way?",
            "Sometimes the reason behind something is more interesting than the answer itself."
        ]


    # ======================
    # CASUAL
    # ======================

    else:

        responses = [
            "Oh, really? 😄 Tell me more.",
            "That's interesting. What happened next?",
            "Hmm, I'd like to hear more about that.",
            "Wait, that's actually pretty interesting."
        ]



    response = choice(
        responses
    )



    # ======================
    # PERSONALITY LAYER
    # ======================


    # Humor


    if (
        humor >= 75
        and
        strategy.get(
            "humor_allowed",
            False
        )
    ):


        if random() < 0.3:


            response += choice([

                " 😄",

                " haha",

                " :)"

            ])




    # Playfulness


    if (
        relationship != "stranger"
        and
        closeness >= 50
    ):


        if random() < 0.25:


            response += choice([

                " Don't get too proud though 😏",

                " I knew you had it in you.",

                " See? I told you."

            ])




    # ======================
    # Question system
    # ======================


    if strategy.get(
        "ask_question",
        False
    ):


        questions = {


            "celebrate":[

                "How did it go?",

                "What was the hardest part?",

                "Are you happy with the result?"

            ],


            "seek_support":[

                "What worries you the most?",

                "Do you want to talk about it?",

                "What part feels the hardest right now?"

            ],


            "normal_conversation":[

                "What do you like about it?",

                "How did you get interested in that?",

                "What fascinates you about it?"

            ],


            "casual_chat":[

                "How has your day been?",

                "What have you been up to?",

                "Anything interesting happen today?"

            ]

        }



        if intent in questions:


            response += " " + choice(
                questions[intent]
            )



    return response