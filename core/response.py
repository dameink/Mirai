from core.llm import ask_llm
from core.prompt import build_prompt
from core.conversation import add_message, get_history


# =========================================
# CONFIGURATION
# =========================================

CONVERSATION_HISTORY_LIMIT = 30


# =========================================
# RESPONSE GENERATOR
# =========================================

def generate_response(
    message,
    context=None,
    strategy=None,
    voice=None,
    user_id=None,
    db=None,
):
    """
    Generate Mirai's response using the canonical
    response pipeline.

    Context contains:
        - memory
        - emotion
        - relationship
        - learning
        - conversation
        - language
        - mode

    Conversation history is passed separately
    from the system prompt.
    """

    message = (message or "").strip()

    if not message:
        return "Hmm... you didn't say anything."

    # =====================================
    # CONTEXT
    # =====================================

    context = context or {}
    strategy = strategy or {}

    emotion = context.get(
        "emotion",
        {},
    )

    relationship = context.get(
        "relationship",
        {},
    )

    memory = context.get(
        "memory",
        {},
    )

    learning = context.get(
        "learning",
        {},
    )

    language = context.get(
        "language",
    )

    mode = context.get(
        "mode",
        "CASUAL_CONVERSATION",
    )

    # =====================================
    # CONVERSATION HISTORY
    #
    # Prefer history already prepared by
    # core.mirai.py.
    #
    # Only query the database if it was
    # not provided.
    # =====================================

    conversation = context.get(
        "conversation"
    )

    if conversation is None:
        conversation = get_history(
            limit=CONVERSATION_HISTORY_LIMIT,
            user_id=user_id,
            db=db,
        )

    # =====================================
    # BUILD SYSTEM PROMPT
    #
    # Only Mirai identity, rules and
    # current state/context go here.
    #
    # Conversation history and current
    # user message remain separate.
    # =====================================

    system_prompt = build_prompt(
        context={
            "memory": memory,
            "emotion": emotion,
            "relationship": relationship,
            "learning": learning,
            "language": language,
            "mode": mode,
        },
        strategy=strategy,
        voice=voice,
    )

    # =====================================
    # ASK LLM
    #
    # Structured message flow:
    #
    # system
    #   ↓
    # previous conversation
    #   ↓
    # current user message
    #
    # Current message is NOT duplicated
    # inside the system prompt.
    # =====================================

    response = ask_llm(
        system_prompt=system_prompt,
        conversation=conversation,
        user_message=message,
    )

    # =====================================
    # PERSIST CONVERSATION
    #
    # Save only after successful response
    # generation.
    # =====================================

    add_message(
        "user",
        message,
        user_id=user_id,
        db=db,
    )

    add_message(
        "assistant",
        response,
        user_id=user_id,
        db=db,
    )

    return response