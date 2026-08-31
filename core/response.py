from core.emotion import (
    change_emotion,
    get_emotion,
    analyze_emotion
)

from core.llm import ask_llm
from core.prompt import build_prompt

from core.memory import (
    remember_semantic,
    get_memory
)

from core.conversation import (
    add_message,
    get_history
)

from core.relationship import (
    get_relationship,
    change_relationship
)


def generate_response(
    message,
    context=None,
    strategy=None,
    voice=None
):
    message = message.strip()

    if not message:
        return "Hmm... you didn't say anything."


    # =========================================
    # 1. SAVE USER MESSAGE
    # =========================================

    add_message(
        "user",
        message
    )


    # =========================================
    # 2. ANALYZE USER EMOTION
    # =========================================

    detected_emotion = analyze_emotion(message)


    if detected_emotion:

        emotion = detected_emotion["emotion"]
        intensity = detected_emotion["intensity"]

        if emotion == "anxiety":
            change_emotion("stress", intensity * 0.05)

        elif emotion == "happiness":
            change_emotion("happiness", intensity * 0.03)
            change_emotion("excitement", intensity * 0.02)

        elif emotion == "sadness":
            change_emotion("happiness", -intensity * 0.03)
            change_emotion("comfort", intensity * 0.02)


    # =========================================
    # 3. MIRAI'S NATURAL EMOTIONAL CHANGE
    # =========================================

    change_emotion(
        "energy",
        -1
    )

    change_emotion(
        "curiosity",
        1
    )


    # =========================================
    # 4. UPDATE RELATIONSHIP
    # =========================================

    change_relationship(
        "familiarity",
        0.5
    )

    change_relationship(
        "bond",
        0.2
    )


    # =========================================
    # 5. SIMPLE MEMORY DETECTION
    # =========================================

    lower_message = message.lower()

    if "my name is" in lower_message:

        name = (
            lower_message
            .replace("my name is", "")
            .strip()
        )

        if name:

            remember_semantic(
                content=f"User name is {name}",
                importance=80,
                category="personal"
            )

            change_emotion(
                "trust",
                2
            )

            change_emotion(
                "happiness",
                3
            )

            change_relationship(
                "familiarity",
                3
            )


    # =========================================
    # 6. LOAD MIRAI'S CURRENT STATE
    # =========================================

    history = get_history(
        limit=10
    )

    memory = get_memory()

    emotion = get_emotion()

    relationship = get_relationship()


    # =========================================
    # 7. BUILD FULL CONTEXT
    # =========================================

    prompt = build_prompt(
        message=message,
        context={
            "conversation": history,
            "memory": memory,
            "emotion": emotion,
            "relationship": relationship
        },
        strategy=strategy,
        voice=voice
    )


    # =========================================
    # 8. ASK LLM
    # =========================================

    response = ask_llm(
        prompt
    )


    # =========================================
    # 9. SAVE MIRAI'S RESPONSE
    # =========================================

    add_message(
        "assistant",
        response
    )


    return response