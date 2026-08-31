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

from core.emotion import (
    get_emotion,
    reset_emotion
)

from core.relationship import (
    get_relationship,
    reset_relationship
)

# ==========================
# LEARNING SYSTEM
# ==========================

from learning.learner import Learner
from core.learning_bridge import LearningBridge
from core.learning_context import LearningContext


# =========================================================
# LEARNING SYSTEM INITIALIZATION
# =========================================================

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


# =========================================================
# MEMORY EXTRACTION
# =========================================================

def process_memory(message):

    text = message.lower().strip()

    # -------------------------
    # I LIKE ...
    # -------------------------

    if text.startswith("i like "):

        memory = get_memory()

        name = (
            memory.get("user_name")
            or "User"
        )

        thing = text.replace(
            "i like ",
            "",
            1
        ).strip()

        if thing:

            remember_semantic(
                content=f"{name} likes {thing}",
                importance=50,
                category="interest"
            )


# =========================================================
# COMMAND HELP
# =========================================================

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


# =========================================================
# STATUS
# =========================================================

def show_status():

    state = get_mirai_state()

    print("\n===== EMOTION =====")
    print(
        state.get(
            "emotion",
            {}
        )
    )

    print("\n===== RELATIONSHIP =====")
    print(
        state.get(
            "relationship",
            {}
        )
    )

    print("\n===== BEHAVIOR =====")
    print(
        state.get(
            "behavior",
            {}
        )
    )

    print("\n===== MEMORY =====")
    print(
        state.get(
            "memory",
            {}
        )
    )

    print("\n===== LEARNING =====")

    print(
        learning_context.get_context()
    )


# =========================================================
# DEBUG
# =========================================================

def debug():

    state = get_mirai_state()

    for key, value in state.items():

        print(
            "\n",
            key.upper()
        )

        print(value)

    print("\nLEARNING CONTEXT")

    print(
        learning_context.get_context()
    )


# =========================================================
# COMMAND PROCESSOR
# =========================================================

def process_command(message):

    # -------------------------
    # MEMORY
    # -------------------------

    if message == "/memory":

        print(
            get_memory()
        )

        return True


    # -------------------------
    # LEARNING
    # -------------------------

    if message == "/learning":

        print(
            learning_context.get_context()
        )

        return True


    # -------------------------
    # STATUS
    # -------------------------

    if message == "/status":

        show_status()

        return True


    # -------------------------
    # DEBUG
    # -------------------------

    if message == "/debug":

        debug()

        return True


    # -------------------------
    # RESET MEMORY
    # -------------------------

    if message == "/reset_memory":

        clear_memory()

        print(
            "Memory cleared."
        )

        return True


    # -------------------------
    # RESET EMOTION
    # -------------------------

    if message == "/reset_emotion":

        reset_emotion()

        print(
            "Emotion reset."
        )

        return True


    # -------------------------
    # RESET RELATIONSHIP
    # -------------------------

    if message == "/reset_relationship":

        reset_relationship()

        print(
            "Relationship reset."
        )

        return True


    # -------------------------
    # RESET ALL
    # -------------------------

    if message == "/reset_all":

        clear_memory()

        reset_emotion()

        reset_relationship()

        clear_conversation()

        print(
            "All systems reset."
        )

        return True


    # -------------------------
    # HELP
    # -------------------------

    if message == "/help":

        show_help()

        return True


    # -------------------------
    # FORGET
    # -------------------------

    if message.startswith("/forget"):

        keyword = (
            message
            .replace(
                "/forget",
                "",
                1
            )
            .strip()
        )

        if not keyword:

            print(
                "Please specify what I should forget."
            )

            return True


        result = forget_semantic(
            keyword
        )


        if result:

            print(
                "Memory forgotten."
            )

        else:

            print(
                "I couldn't find that memory."
            )

        return True


    return False


# =========================================================
# MAIN CHAT
# =========================================================

def chat(message):

    message = message.strip()

    if not message:

        return {
            "response": "",
            "state": get_mirai_state()
        }


    # =====================================================
    # 1. MEMORY EXTRACTION
    # =====================================================

    process_memory(
        message
    )


    # =====================================================
    # 2. LEARNING PROCESSING
    # =====================================================
    #
    # This is where the message enters the learning system.
    #
    # It can detect:
    # - learning goals
    # - learning requests
    # - exam preparation
    # - progress
    # - failure
    #
    # and update the learner.
    # =====================================================

    learning_result = (
        learning_context
        .process_message(
            message
        )
    )


    # =====================================================
    # 3. SOCIAL PROCESSING
    # =====================================================
    #
    # Updates:
    # - relationship
    # - emotional/social state
    # - interaction information
    # =====================================================

    try:

        process_social_interaction(
            message
        )

    except TypeError:

        # If the current social_brain expects
        # additional arguments, try using the
        # existing interface.

        try:

            process_social_interaction(
                message,
                None
            )

        except Exception:

            pass

    except Exception:

        pass


    # =====================================================
    # 4. BUILD MIRAI RESPONSE CONTEXT
    # =====================================================
    #
    # This collects the existing Mirai systems:
    #
    # memory
    # emotion
    # relationship
    # personality
    # behavior
    # etc.
    # =====================================================

    context = get_response_context(
        message
    )


    # =====================================================
    # 5. ADD LEARNING TO CONTEXT
    # =====================================================
    #
    # Learning is NOT separate from the conversation.
    #
    # It becomes part of the context used to decide
    # how Mirai should respond.
    # =====================================================

    try:

        learning_profile = (
            learning_context
            .get_context()
        )

    except Exception:

        learning_profile = (
            learner.get_profile()
        )


    try:

        learning_influence = (
            learning_bridge
            .get_learning_influence(
                message,
                learning_context
            )
        )

    except Exception:

        learning_influence = {}


    context["learning"] = {

        "profile":
            learning_profile,

        "influence":
            learning_influence

    }


    # =====================================================
    # 6. CURRENT MIRAI STATE
    # =====================================================

    state = get_mirai_state()


    # =====================================================
    # 7. RESPONSE STRATEGY
    # =====================================================
    #
    # The response engine now sees BOTH:
    #
    # Mirai's state
    # +
    # learner's state
    #
    # and decides how Mirai should respond.
    # =====================================================

    strategy = choose_response_strategy(
        context
    )


    # =====================================================
    # 8. PERSONALITY VOICE
    # =====================================================
    #
    # Personality determines HOW Mirai says it.
    # =====================================================

    voice = get_personality_voice(
        context,
        strategy
    )


    # =====================================================
    # 9. BUILD FINAL PROMPT
    # =====================================================
    #
    # The prompt receives:
    #
    # user message
    # Mirai context
    # learning context
    # response strategy
    # personality voice
    # =====================================================

    prompt = build_prompt(
        message,
        context,
        strategy,
        voice
    )


    # =====================================================
    # 10. LLM
    # =====================================================

    response = ask_llm(
        prompt
    )


    # =====================================================
    # 11. SAVE CONVERSATION
    # =====================================================

    add_message(
        "user",
        message
    )

    add_message(
        "assistant",
        response
    )


    # =====================================================
    # 12. GET UPDATED STATE
    # =====================================================
    #
    # Important:
    # state is obtained AFTER processing the message,
    # so frontend receives the updated state.
    # =====================================================

    chat_state = {

        "emotion":
            get_emotion()["state"],

        "relationship":
            get_relationship(),

        "learning":
            learner.get_profile()

    }


    # =====================================================
    # 13. RETURN EVERYTHING
    # =====================================================

    return {

        "message":
            message,

        "response":
            response,

        "context":
            context,

        "strategy":
            strategy,

        "voice":
            voice,

        "learning":
            learning_result,

        "state":
            chat_state

    }


# =========================================================
# TERMINAL CHAT
# =========================================================

if __name__ == "__main__":

    print(
        "Mirai is ready."
    )

    print(
        "Type /help for commands."
    )


    while True:

        message = input(
            "\nYou: "
        ).strip()


        if message.lower() == "exit":

            print(
                "Goodbye!"
            )

            break


        # =================================================
        # COMMANDS
        # =================================================

        if process_command(
            message
        ):

            continue


        # =================================================
        # CHAT
        # =================================================

        try:

            result = chat(
                message
            )

            print(
                "\nMirai:",
                result["response"]
            )

        except Exception as e:

            print(
                "\nMirai error:",
                str(e)
            )