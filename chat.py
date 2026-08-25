from core.llm import ask_llm
from core.prompt import build_prompt

from core.memory import (
    remember_semantic,
    clear_memory,
    get_memory,
    forget_semantic
)

from core.brain import get_mirai_state

from core.conversation import (
    add_message,
    clear_conversation
)

from core.social_brain import process_social_interaction

from core.response_engine import (
    get_response_context,
    choose_response_strategy
)

from core.personality_voice import get_personality_voice

from core.emotion import reset_emotion
from core.relationship import reset_relationship


# ==========================
# LEARNING SYSTEM
# ==========================

from learning.learner import Learner
from core.learning_bridge import LearningBridge
from core.learning_context import LearningContext



# Create learning system

learner = Learner(
    native_language="",
    learning_language="English"
)


learning_bridge = LearningBridge(
    learner
)


learning_context = LearningContext(
    learning_bridge
)


# ==========================
# MEMORY EXTRACTION
# ==========================


def process_memory(message):

    text = message.lower()


    if text.startswith("i like"):

        memory = get_memory()

        name = (
            memory.get("user_name")
            or "User"
        )


        thing = text.replace(
            "i like ",
            ""
        )


        remember_semantic(
            content=f"{name} likes {thing}",
            importance=50,
            category="interest"
        )



# ==========================
# DEBUG
# ==========================


def show_status():

    state = get_mirai_state()


    print("\n===== EMOTION =====")
    print(state["emotion"])


    print("\n===== RELATIONSHIP =====")
    print(state["relationship"])


    print("\n===== BEHAVIOR =====")
    print(state["behavior"])


    print("\n===== MEMORY =====")
    print(state["memory"])



    print("\n===== LEARNING =====")

    print(
        learning_context.get_context()
    )



def debug():

    state = get_mirai_state()


    for key,value in state.items():

        print(
            "\n",
            key.upper()
        )

        print(value)



    print("\nLEARNING CONTEXT")

    print(
        learning_context.get_context()
    )



# ==========================
# COMMANDS
# ==========================


def show_help():

    print("""
Mirai commands:

/memory
/status
/debug

/learning

/reset_memory
/reset_emotion
/reset_relationship
/reset_all

/forget <fact>

exit

""")



# ==========================
# MAIN LOOP
# ==========================


while True:


    message = input(
        "You: "
    )



    if message == "exit":
        break



    # ======================
    # COMMANDS
    # ======================


    if message == "/memory":

        print(
            get_memory()
        )

        continue



    if message == "/learning":

        print(
            learning_context.get_context()
        )

        continue



    if message == "/status":

        show_status()

        continue



    if message == "/debug":

        debug()

        continue



    if message == "/reset_memory":

        clear_memory()

        print(
            "Memory cleared."
        )

        continue



    if message == "/reset_emotion":

        reset_emotion()

        print(
            "Emotion reset."
        )

        continue



    if message == "/reset_relationship":

        reset_relationship()

        print(
            "Relationship reset."
        )

        continue



    if message == "/reset_all":

        clear_memory()

        reset_emotion()

        reset_relationship()

        clear_conversation()

        print(
            "All systems reset."
        )

        continue



    if message == "/help":

        show_help()

        continue



    if message.startswith("/forget"):

        keyword = (
            message
            .replace("/forget", "")
            .strip()
        )


        result = forget_semantic(
            keyword
        )


        if result:
            print("Memory forgotten.")

        else:
            print("I couldn't find that memory.")


        continue



    # ======================
    # MEMORY
    # ======================


    process_memory(
        message
    )



    # ======================
    # SOCIAL UPDATE
    # ======================


    process_social_interaction(
        message
    )



    # ======================
    # MIRAI CONTEXT
    # ======================


    context = get_response_context(
        message
    )



    # ======================
    # ADD LEARNING CONTEXT
    # ======================

    learning_influence = learning_bridge.get_learning_influence(
        message,
        learning_context
    )

    context["learning"] = {

        "profile":
            learning_context.get_context(),


        "influence":
            learning_bridge.get_learning_influence(
                message,
                learning_context
            )

    }



    # ======================
    # RESPONSE STRATEGY
    # ======================


    strategy = choose_response_strategy(
        context
    )



    #print("\nSTRATEGY:")
    #print(strategy)



    # ======================
    # PERSONALITY VOICE
    # ======================


    voice = get_personality_voice(
        context,
        strategy
    )


   # print("\nVOICE:")
    #print(voice)



    # ======================
    # PROMPT
    # ======================


    prompt = build_prompt(
        message,
        context,
        strategy,
        voice
    )



    # ======================
    # LLM
    # ======================


    response = ask_llm(
        prompt
    )



    print(
        "\nMirai:",
        response
    )



    # ======================
    # SAVE CONVERSATION
    # ======================


    add_message(
        "user",
        message
    )


    add_message(
        "assistant",
        response
    )