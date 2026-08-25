from core.response_engine import get_response_context, choose_response_strategy
from core.personality_voice import get_personality_voice
from core.prompt import build_prompt
from core.llm import ask_llm


TEST_MESSAGES = [

    # =====================================
    # SADNESS / LONELINESS
    # =====================================

    "Sometimes I feel really lonely even when I'm surrounded by people.",

    "I feel like nobody really understands me.",

    "Recently I feel like I lost motivation to do anything.",

    "I don't know why, but I feel empty today.",


    # =====================================
    # FAILURE / SELF DOUBT
    # =====================================

    "I failed my math exam and I feel like I'm not good enough.",

    "I studied so hard but still failed. Maybe I'm just not smart enough.",

    "I feel like everyone is better than me.",

    "I'm scared that I will never achieve my goals.",


    # =====================================
    # DEEP PERSONAL THOUGHTS
    # =====================================

    "Sometimes I wonder if I'm wasting my time in life.",

    "I want to do something meaningful, but I don't know if I can.",

    "I feel like people only see the surface of who I am.",


    # =====================================
    # SEEKING SUPPORT
    # =====================================

    "I had a really bad day today.",

    "Can I tell you something? I haven't been feeling great lately.",

    "I just need someone to talk to right now.",


    # =====================================
    # RECOVERY / POSITIVE AFTER SADNESS
    # =====================================

    "Actually, I think I'm starting to feel better now.",

    "I talked with my friend and it helped a little.",

    "Maybe things are not as bad as I thought."

]


for message in TEST_MESSAGES:


    print("\n")
    print("=" * 60)

    print("USER:")
    print(message)


    # Context

    context = get_response_context(
        message
    )


    # Strategy

    strategy = choose_response_strategy(
        context
    )


    # Voice

    voice = get_personality_voice(
        context,
        strategy
    )


    print("\nSTRATEGY:")
    print(strategy)


    print("\nVOICE RULES:")
    for rule in voice["active_rules"]:
        print("-", rule)


    # Prompt

    prompt = build_prompt(
        message,
        context,
        strategy,
        voice
    )


    # Response

    response = ask_llm(
        prompt
    )


    print("\nMIRAI:")
    print(response)


    print("=" * 60)