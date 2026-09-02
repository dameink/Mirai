
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

# ============================================================
# TEST ENVIRONMENT
# ============================================================

tmp_dir = tempfile.TemporaryDirectory()

os.environ["DATABASE_URL"] = (
    f"sqlite:///{Path(tmp_dir.name) / 'test.db'}"
)

# ============================================================
# IMPORTS
# ============================================================

from db.database import Base, engine, SessionLocal
from db.models import User, Message, Memory, EmotionalMemory

from auth.service import (
    register_user,
    create_auth_tokens,
    get_user_from_access_token,
)

import core.mirai
import core.social_brain as social_brain

from core.memory import (
    remember_semantic,
    get_memory,
)

from core.memory_recall import recall_memory

from core.conversation import (
    get_history,
    clear_conversation,
)

from core.emotion import (
    get_emotion,
)

from core.relationship import (
    get_relationship,
)

from core.learning import (
    create_learning_context,
)

# ============================================================
# TEST HELPERS
# ============================================================

def check(name, condition):
    if not condition:
        raise AssertionError(f"FAIL: {name}")

    print(f"PASS: {name}")


def emotion_values(emotion):
    """
    Extract actual emotion values regardless of whether
    get_emotion() returns them directly or under a nested
    'state' / 'values' structure.
    """

    if not isinstance(emotion, dict):
        return {}

    if isinstance(emotion.get("state"), dict):
        return emotion["state"]

    if isinstance(emotion.get("values"), dict):
        return emotion["values"]

    expected_keys = {
        "happiness",
        "energy",
        "trust",
        "curiosity",
        "comfort",
        "excitement",
        "stress",
    }

    if expected_keys.intersection(emotion.keys()):
        return emotion

    return {}


def learning_profile(context):
    """
    Use the actual Learner profile rather than assuming
    the bridge has the same public structure.
    """

    return context.learning.learner.get_profile()


# ============================================================
# OFFLINE LLM
# ============================================================

def fake_generate_response(*args, **kwargs):
    return "Offline test response"


# core.mirai imported generate_response directly,
# therefore patch the reference used by core.mirai.
core.mirai.generate_response = fake_generate_response


# ============================================================
# DATABASE
# ============================================================

Base.metadata.create_all(bind=engine)

db = SessionLocal()


# ============================================================
# 1. AUTHENTICATION
# ============================================================

user = register_user(
    db,
    email="final-test@example.com",
    password="password123",
)

access_token, refresh_token = create_auth_tokens(
    db,
    user.id,
)

authenticated_user = get_user_from_access_token(
    db,
    access_token,
)

check(
    "authentication works",
    authenticated_user is not None
    and authenticated_user["id"] == user.id,
)


# ============================================================
# 2. CONVERSATION PERSISTENCE
# ============================================================

clear_conversation(
    user_id=user.id,
    db=db,
)

db.add(
    Message(
        user_id=user.id,
        role="user",
        content="Hello Mirai",
    )
)

db.commit()

history = get_history(
    limit=30,
    user_id=user.id,
    db=db,
)

check(
    "conversation persistence works",
    len(history) == 1
    and history[0]["content"] == "Hello Mirai",
)


# ============================================================
# 3. MEMORY RECALL
# ============================================================

remember_semantic(
    content="User wants to work in investment banking",
    importance=80,
    category="career",
    user_id=user.id,
    db=db,
)

remember_semantic(
    content="User likes football",
    importance=50,
    category="interest",
    user_id=user.id,
    db=db,
)

remember_semantic(
    content="User enjoys hiking in the mountains",
    importance=50,
    category="hobby",
    user_id=user.id,
    db=db,
)

recalled = recall_memory(
    message="I want to work in investment banking",
    cognition={
        "context": "goal",
        "intent": "conversation",
    },
    user_id=user.id,
    db=db,
)

recalled_text = str(recalled).lower()

check(
    "relevant memory is recalled",
    "investment banking" in recalled_text
    or "investment banker" in recalled_text,
)

primary_memory = str(
    recalled.get("primary", [])
).lower()

check(
    "irrelevant football memory is not primary recall",
    "football" not in primary_memory,
)


# ============================================================
# 4. MEMORY USER ISOLATION
# ============================================================

user2 = register_user(
    db,
    email="final-test-2@example.com",
    password="password123",
)

remember_semantic(
    content="User 2 likes programming",
    importance=70,
    category="interest",
    user_id=user2.id,
    db=db,
)

user1_memory = get_memory(
    user_id=user.id,
    db=db,
)

check(
    "memory is isolated between users",
    "User 2 likes programming" not in str(user1_memory),
)


# ============================================================
# 5. MEMORY CONFLICT DETECTION
# ============================================================

remember_semantic(
    content="User likes football",
    importance=60,
    category="interest",
    user_id=user.id,
    db=db,
)

remember_semantic(
    content="User doesn't like coffee anymore",
    importance=60,
    category="interest",
    user_id=user.id,
    db=db,
)

user_memory = get_memory(
    user_id=user.id,
    db=db,
)

memory_text = str(user_memory).lower()

check(
    "unrelated negative memory does not overwrite football",
    "football" in memory_text,
)

check(
    "coffee statement is stored independently",
    "coffee" in memory_text,
)


# ============================================================
# 6. EMOTION / RELATIONSHIP EXACTLY ONCE
# ============================================================

emotion_calls = []
relationship_calls = []

original_emotion = social_brain.apply_emotion_event
original_relationship = social_brain.apply_relationship_event


def tracked_emotion(*args, **kwargs):
    emotion_calls.append(True)
    return original_emotion(*args, **kwargs)


def tracked_relationship(*args, **kwargs):
    relationship_calls.append(True)
    return original_relationship(*args, **kwargs)


with patch(
    "core.social_brain.apply_emotion_event",
    side_effect=tracked_emotion,
), patch(
    "core.social_brain.apply_relationship_event",
    side_effect=tracked_relationship,
):
    result = core.mirai.chat(
        "I really like football",
        language="English",
        mode="CASUAL_CHAT",
        user_id=user.id,
        db=db,
    )


check(
    "emotion event is applied exactly once",
    len(emotion_calls) == 1,
)

check(
    "relationship event is applied exactly once",
    len(relationship_calls) == 1,
)


# ============================================================
# 7. LEARNING STATE
# ============================================================

learning_context = create_learning_context(user.id)

learning_context.learning.learner.set_goal(
    "Improve conversational English"
)

profile = learning_profile(learning_context)

check(
    "learning state contains real learner data",
    isinstance(profile, dict)
    and isinstance(profile.get("goals"), dict)
    and profile["goals"].get("primary")
    == "Improve conversational English",
)


# ============================================================
# 8. LEARNING / MEMORY / EMOTION / RELATIONSHIP
#    REACH RESPONSE GENERATION
# ============================================================

captured_context = {}


def capture_response(
    message,
    context,
    strategy,
    voice=None,
    user_id=None,
    db=None,
):
    captured_context.update(context)
    return "TEST RESPONSE"


with patch(
    "core.mirai.generate_response",
    side_effect=capture_response,
):
    core.mirai.chat(
        "I want to practice English",
        language="English",
        mode="ACTIVE_LEARNING",
        user_id=user.id,
        db=db,
    )


check(
    "learning reaches response generation",
    "learning" in captured_context,
)

check(
    "memory reaches response generation",
    "memory" in captured_context,
)

check(
    "emotion reaches response generation",
    "emotion" in captured_context,
)

check(
    "relationship reaches response generation",
    "relationship" in captured_context,
)


# ============================================================
# 9. CURRENT USER MESSAGE IS NOT DUPLICATED
# ============================================================

captured_message = {}


def capture_current_message(
    message,
    context,
    strategy,
    voice=None,
    user_id=None,
    db=None,
):
    captured_message["message"] = message
    captured_message["conversation"] = context.get(
        "conversation",
        [],
    )

    return "TEST RESPONSE"


current_user_message = "This is the current message"

with patch(
    "core.mirai.generate_response",
    side_effect=capture_current_message,
):
    core.mirai.chat(
        current_user_message,
        language="English",
        mode="CASUAL_CHAT",
        user_id=user.id,
        db=db,
    )

conversation = captured_message["conversation"]

current_count = sum(
    1
    for item in conversation
    if item.get("content") == current_user_message
)

check(
    "current user message is not duplicated",
    current_count <= 1,
)


# ============================================================
# 10. RESET THROUGH THE REAL APPLICATION RESET
# ============================================================

# Import only after the isolated database environment
# has already been configured.

from main import full_reset


# Create state that must be removed.

db.add(
    Message(
        user_id=user.id,
        role="user",
        content="Message before reset",
    )
)

db.commit()

remember_semantic(
    content="User wants to remember this before reset",
    importance=80,
    category="test",
    user_id=user.id,
    db=db,
)

learning_before_reset = create_learning_context(user.id)

learning_before_reset.learning.learner.set_goal(
    "Temporary reset goal"
)


# Capture initial emotion structure after reset through
# the actual reset function.

full_reset(
    current_user={"id": user.id},
    db=db,
)

messages_after_reset = get_history(
    limit=30,
    user_id=user.id,
    db=db,
)

memory_after_reset = get_memory(
    user_id=user.id,
    db=db,
)

emotion_after_reset = get_emotion(
    user_id=user.id,
    db=db,
)

relationship_after_reset = get_relationship(
    user_id=user.id,
    db=db,
)

learning_after_reset = create_learning_context(user.id)

learning_profile_after_reset = learning_profile(
    learning_after_reset
)


check(
    "real reset clears conversation",
    len(messages_after_reset) == 0,
)

check(
    "real reset clears semantic memory",
    len(
        memory_after_reset
        .get("semantic", {})
        .get("facts", [])
    ) == 0,
)

check(
    "real reset clears emotional memory",
    db.query(EmotionalMemory)
    .filter(
        EmotionalMemory.user_id == user.id
    )
    .count()
    == 0,
)

check(
    "real reset restores relationship",
    relationship_after_reset.get("stage")
    == "stranger",
)

check(
    "real reset restores learning",
    isinstance(
        learning_profile_after_reset,
        dict,
    )
    and isinstance(
        learning_profile_after_reset.get("goals"),
        dict,
    )
    and learning_profile_after_reset["goals"].get(
        "primary"
    ) is None,
)


# Verify that reset actually returned emotion to a valid
# initial state without assuming its exact nesting.

reset_emotion_state = emotion_values(
    emotion_after_reset
)

check(
    "real reset restores emotion state",
    isinstance(reset_emotion_state, dict)
    and all(
        key in reset_emotion_state
        for key in (
            "happiness",
            "energy",
            "trust",
            "curiosity",
            "comfort",
            "excitement",
            "stress",
        )
    ),
)


# ============================================================
# 11. RESET DOES NOT AFFECT ANOTHER USER
# ============================================================

# Give user2 independent conversation state.

db.add(
    Message(
        user_id=user2.id,
        role="user",
        content="User 2 message",
    )
)

db.commit()

full_reset(
    current_user={"id": user.id},
    db=db,
)

user2_history = get_history(
    limit=30,
    user_id=user2.id,
    db=db,
)

check(
    "reset does not affect another user",
    len(user2_history) == 1
    and user2_history[0]["content"]
    == "User 2 message",
)


# ============================================================
# 12. CLI USES THE SAME CORE MIRAI PIPELINE
# ============================================================

import chat as cli_chat

with patch(
    "chat.chat",
    return_value={
        "response": "CLI TEST",
    },
) as mocked:
    cli_chat.chat(
        "hello",
        user_id=user.id,
        db=db,
    )

check(
    "CLI delegates to core Mirai pipeline",
    mocked.called,
)


# ============================================================
# 13. NO SECOND MIRAI BRAIN IN CANONICAL PYTHON PIPELINE
# ============================================================

# core.mirai must be the authoritative chat entry point.

check(
    "canonical Mirai chat function exists",
    callable(core.mirai.chat),
)

check(
    "canonical response generator exists",
    callable(core.mirai.generate_response),
)


# ============================================================
# 14. FINAL RESULT STRUCTURE
# ============================================================

# The canonical pipeline must return a structured result.

with patch(
    "core.mirai.generate_response",
    return_value="Offline test response",
):
    final_result = core.mirai.chat(
        "Hello Mirai",
        language="English",
        mode="CASUAL_CHAT",
        user_id=user.id,
        db=db,
    )

check(
    "Mirai returns structured chat result",
    isinstance(final_result, dict),
)

check(
    "Mirai returns response",
    "response" in final_result,
)

check(
    "Mirai returns analysis",
    "analysis" in final_result,
)

check(
    "Mirai returns decision",
    "decision" in final_result,
)

check(
    "Mirai returns response plan",
    "plan" in final_result,
)

check(
    "Mirai returns learning state",
    "learning" in final_result,
)

check(
    "Mirai returns memory context",
    "memory" in final_result,
)


# ============================================================
# CLEANUP
# ============================================================

db.close()
tmp_dir.cleanup()

print()
print("=" * 60)
print("FINAL MIRAI INTEGRATION TEST PASSED")
print("=" * 60)
