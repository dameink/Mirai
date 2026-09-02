from core.analyzer import analyze_message
from core.brain import get_mirai_state

from core.decision import make_decision
from core.response_plan import create_response_plan
from core.response import generate_response

from core.social_brain import process_social_interaction

from core.emotion import get_emotion
from core.relationship import get_relationship

from core.conversation import get_history

from core.learning import create_learning_context

from core.memory import remember_semantic
from core.memory_recall import recall_memory


# ============================================
# MEMORY
# ============================================

def process_memory(
    message,
    user_id=None,
    db=None,
):
    """
    Process explicit user memories.

    Memory persistence is handled by core.memory.
    Memory recall is handled separately by core.memory_recall.
    """

    if not message:
        return

    text = message.lower().strip()

    # ----------------------------------------
    # USER LIKES SOMETHING
    # ----------------------------------------

    if text.startswith("i like "):
        thing = text[len("i like "):].strip()

        if thing:
            remember_semantic(
                content=f"User likes {thing}",
                importance=50,
                category="interest",
                user_id=user_id,
                db=db,
            )


# ============================================
# MAIN MIRAI PIPELINE
# ============================================

def chat(
    message,
    language=None,
    mode=None,
    user_id=None,
    db=None,
):
    """
    Canonical Mirai processing pipeline.

    User
        ↓
    Memory write
        ↓
    Analysis
        ↓
    Memory recall
        ↓
    Learning
        ↓
    Social processing
        ↓
    State
        ↓
    Decision
        ↓
    Response plan
        ↓
    Response generation
        ↓
    LLM
        ↓
    Persistence
    """

    message = (message or "").strip()

    # ========================================
    # VALIDATION
    # ========================================

    if db is None:
        raise ValueError("db is required")

    if not user_id:
        raise ValueError("user_id is required")

    # ========================================
    # EMPTY MESSAGE
    # ========================================

    if not message:
        return {
            "message": "",
            "response": "",
            "state": get_mirai_state(
                user_id=user_id,
                db=db,
            ),
        }

    # ========================================
    # 1. MEMORY WRITE
    # ========================================

    process_memory(
        message,
        user_id=user_id,
        db=db,
    )

    # ========================================
    # 2. UNDERSTAND USER
    # ========================================

    analysis = analyze_message(
        message,
        user_id=user_id,
        db=db,
    )

    # ========================================
    # 3. MEMORY RECALL
    #
    # Only ranked relevant memories are
    # passed forward to the response system.
    # ========================================

    memory_recall = recall_memory(
        message=message,
        cognition=analysis.get("cognition"),
        user_id=user_id,
        db=db,
    )

    # ========================================
    # 4. LEARNING CONTEXT
    # ========================================

    learning_context = create_learning_context(
        user_id=user_id,
    )

    # ========================================
    # 5. LEARNING
    #
    # Learning is processed exactly once.
    # ========================================

    learning_result = learning_context.process_message(
        message,
        context=analysis,
    )

    learning = learning_context.get_context()

    # ========================================
    # 6. SOCIAL BRAIN
    #
    # Authoritative mutation point for:
    # - emotion
    # - relationship
    #
    # These states must not be mutated
    # elsewhere in the pipeline.
    # ========================================

    process_social_interaction(
        message,
        user_id=user_id,
        db=db,
    )

    # ========================================
    # 7. CURRENT STATE
    #
    # Read AFTER social processing.
    # ========================================

    state = get_mirai_state(
        user_id=user_id,
        db=db,
    )

    # ========================================
    # 8. DECISION
    # ========================================

    decision = make_decision(
        message,
        analysis,
        user_id=user_id,
        db=db,
    )

    # ========================================
    # 9. RESPONSE PLAN
    # ========================================

    plan = create_response_plan(
        cognition=analysis.get("cognition"),
        emotion=analysis.get("emotion"),
        memory=memory_recall,
        decision=decision,
    )

    # ========================================
    # 10. CONVERSATION HISTORY
    #
    # Previous messages only.
    # Current user message is passed separately
    # by response.py.
    # ========================================

    conversation = get_history(
        limit=30,
        user_id=user_id,
        db=db,
    )

    # ========================================
    # 11. RESPONSE GENERATION
    # ========================================

    response = generate_response(
        message=message,

        context={
            # Previous conversation
            "conversation": conversation,

            # Only relevant recalled memories
            "memory": memory_recall,

            # Current emotion
            "emotion": get_emotion(
                user_id=user_id,
                db=db,
            ),

            # Current relationship
            "relationship": get_relationship(
                user_id=user_id,
                db=db,
            ),

            # Complete learning state
            "learning": learning,

            # Response language
            "language": language,

            # Conversation mode
            "mode": mode,
        },

        strategy=plan,
        voice=None,

        user_id=user_id,
        db=db,
    )

    # ========================================
    # 12. UPDATED PUBLIC STATE
    # ========================================

    chat_state = {
        "emotion": get_emotion(
            user_id=user_id,
            db=db,
        )["state"],

        "relationship": get_relationship(
            user_id=user_id,
            db=db,
        ),

        "learning": learning_context.learning.get_profile(),
    }

    # ========================================
    # 13. RETURN
    # ========================================

    return {
        "message": message,
        "analysis": analysis,
        "decision": decision,
        "plan": plan,
        "response": response,

        # Full learning state
        "learning": learning,

        # Ranked relevant memories
        "memory": memory_recall,

        # Public Mirai state
        "state": chat_state,
    }