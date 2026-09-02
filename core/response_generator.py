
from random import choice, random


# =========================================================
# HELPERS
# =========================================================

def get_value(context, key, default=0):
    return context.get(
        key,
        default
    )


# =========================================================
# RESPONSE GENERATOR
# =========================================================

def generate_response(strategy, context):

    strategy = strategy or {}
    context = context or {}


    # =====================================================
    # CONTEXT
    # =====================================================

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


    # =====================================================
    # BASE RESPONSES
    # =====================================================

    responses = []


    # =====================================================
    # ENCOURAGING / ACHIEVEMENT
    # =====================================================

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
                "That's a huge step forward. You should take a moment to appreciate it.",
                "Honestly, that's really great news. You worked for this."
            ]

        else:

            responses = [
                "That's amazing! Congratulations 😄",
                "Wow, that's a great achievement. You should be proud of yourself.",
                "That's really great news. Your effort paid off.",
                "Nice! That's definitely something worth celebrating."
            ]


    # =====================================================
    # SUPPORT / FAILURE
    # =====================================================

    elif style == "empathetic":

        if closeness >= 70:

            responses = [
                "Hey... that sounds really rough.",
                "Yeah... I can see why that would hurt.",
                "That's frustrating. I'm sorry you had to deal with that.",
                "Hmm... yeah, that's not easy."
            ]

        elif closeness >= 30:

            responses = [
                "I'm sorry that happened. That must have been disappointing.",
                "Yeah, I understand why that would feel frustrating.",
                "Sometimes things just don't go the way we want.",
                "That sounds tough."
            ]

        else:

            responses = [
                "I'm sorry to hear that.",
                "That sounds frustrating.",
                "Yeah... that's rough.",
                "I can see why that would be disappointing."
            ]


    # =====================================================
    # INTEREST / CURIOSITY
    # =====================================================

    elif style == "interested":

        if curiosity >= 80:

            responses = [
                "Wait, really? That's actually fascinating 😄",
                "Oh, that's interesting. I didn't expect that.",
                "Hmm, that's actually pretty cool.",
                "Okay, now you've got my attention."
            ]

        else:

            responses = [
                "That's interesting.",
                "Hmm, that's pretty cool.",
                "I hadn't thought about it that way.",
                "That's actually worth thinking about."
            ]


    # =====================================================
    # PLAYFUL
    # =====================================================

    elif style == "playful":

        if humor >= 70:

            responses = [
                "Okay, wait... I didn't expect that 😂",
                "Haha, that's actually kind of funny.",
                "Interesting choice 😄",
                "Okay, we're choosing chaos today, apparently."
            ]

        else:

            responses = [
                "Oh, that's unexpected 😄",
                "Really? That's interesting.",
                "I didn't see that coming haha."
            ]


    # =====================================================
    # REFLECTIVE
    # =====================================================

    elif style == "reflective":

        responses = [
            "Hmm... that's actually something worth thinking about.",
            "I think there might be more behind that than the situation itself.",
            "That's an interesting way to look at it.",
            "Sometimes the reason behind something is more interesting than the answer."
        ]


    # =====================================================
    # CASUAL
    # =====================================================

    else:

        responses = [
            "Oh, really? 😄",
            "Hmm, interesting.",
            "Oh, that's pretty interesting.",
            "Wait, really?",
            "I see.",
            "Yeah, that's fair."
        ]


    # =====================================================
    # SAFETY FALLBACK
    # =====================================================

    if not responses:

        responses = [
            "Hmm...",
            "Interesting.",
            "Yeah, I see.",
            "That's fair."
        ]


    response = choice(
        responses
    )


    # =====================================================
    # PERSONALITY — HUMOR
    # =====================================================

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


    # =====================================================
    # PERSONALITY — PLAYFULNESS
    # =====================================================

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


    # =====================================================
    # QUESTION SYSTEM
    # =====================================================

    if strategy.get(
        "ask_question",
        False
    ):

        questions = {

            "celebrate": [
                "How did it go?",
                "What was the hardest part?",
                "Are you happy with the result?"
            ],

            "seek_support": [
                "What worries you the most?",
                "Do you want to talk about it?",
                "What part feels the hardest right now?"
            ],

            "normal_conversation": [
                "What do you like about it?",
                "How did you get interested in that?",
                "What fascinates you about it?"
            ],

            "casual_chat": [
                "How has your day been?",
                "What have you been up to?",
                "Anything interesting happen today?"
            ]

        }


        if intent in questions:

            response += " " + choice(
                questions[intent]
            )


    # =====================================================
    # FINAL
    # =====================================================

    return response
