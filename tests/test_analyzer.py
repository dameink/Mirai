from core.analyzer import analyze_message
from core.memory import clear_memory, remember_semantic
from core.emotion import reset_emotion


def check(name, condition, details=""):
    if condition:
        print(f"✅ PASS — {name}")
        return True

    print(f"❌ FAIL — {name}")

    if details:
        print(f"   {details}")

    return False


results = []


def test(name, condition, details=""):
    results.append(
        check(name, condition, details)
    )


# ============================================
# RESET
# ============================================

print("\n")
print("=" * 70)
print("MIRAI ANALYZER TEST")
print("=" * 70)

clear_memory()
reset_emotion()


# ============================================
# PREPARE MEMORY
# ============================================

remember_semantic(
    "User name is Alex",
    importance=80,
    category="personal"
)

remember_semantic(
    "User wants to become an engineer",
    importance=80,
    category="goal"
)

remember_semantic(
    "User likes football",
    importance=60,
    category="interest"
)


# ============================================
# TEST 1 — BASIC STRUCTURE
# ============================================

print("\n")
print("TEST 1 — BASIC ANALYSIS")

result = analyze_message(
    "What is my name?"
)

print(result)

test(
    "Analyzer returns result",
    isinstance(result, dict)
)

test(
    "Analyzer contains message",
    "message" in result
)

test(
    "Analyzer contains cognition",
    "cognition" in result
)

test(
    "Analyzer contains emotion",
    "emotion" in result
)

test(
    "Analyzer contains memories",
    "memories" in result
)


# ============================================
# TEST 2 — COGNITION
# ============================================

print("\n")
print("TEST 2 — COGNITION")

cognition = result.get("cognition", {})

print(cognition)

test(
    "Cognition is dictionary",
    isinstance(cognition, dict)
)

test(
    "Cognition has context",
    "context" in cognition
)

test(
    "Cognition has intent",
    "intent" in cognition
)

test(
    "Cognition has importance",
    "importance" in cognition
)

test(
    "Question is detected as recall",
    cognition.get("intent") == "recall",
    f"Detected intent: {cognition.get('intent')}"
)


# ============================================
# TEST 3 — MEMORY RECALL
# ============================================

print("\n")
print("TEST 3 — MEMORY RECALL")

memories = result.get("memories")

print(memories)

test(
    "Memory recall returns dictionary",
    isinstance(memories, dict)
)

test(
    "Memory recall contains primary",
    "primary" in memories
)

test(
    "Memory recall contains secondary",
    "secondary" in memories
)


# ============================================
# TEST 4 — NAME MEMORY
# ============================================

print("\n")
print("TEST 4 — NAME MEMORY")

all_memories = (
    memories.get("primary", [])
    +
    memories.get("secondary", [])
)

name_found = any(
    "Alex" in str(item)
    for item in all_memories
)

test(
    "Analyzer recalls user's name",
    name_found,
    f"Recalled memories: {all_memories}"
)


# ============================================
# TEST 5 — GOAL MEMORY
# ============================================

print("\n")
print("TEST 5 — GOAL MEMORY")

goal_result = analyze_message(
    "What is my career goal?"
)

print(goal_result)

goal_memories = (
    goal_result.get("memories", {}).get("primary", [])
    +
    goal_result.get("memories", {}).get("secondary", [])
)

goal_found = any(
    "engineer" in str(item).lower()
    for item in goal_memories
)

test(
    "Analyzer recalls engineering goal",
    goal_found,
    f"Recalled memories: {goal_memories}"
)


# ============================================
# TEST 6 — INTEREST MEMORY
# ============================================

print("\n")
print("TEST 6 — INTEREST FILTER")

interest_result = analyze_message(
    "What hobbies do I like?"
)

print(interest_result)

interest_memories = (
    interest_result.get("memories", {}).get("primary", [])
    +
    interest_result.get("memories", {}).get("secondary", [])
)

football_found = any(
    "football" in str(item).lower()
    for item in interest_memories
)

test(
    "Analyzer recalls football interest",
    football_found,
    f"Recalled memories: {interest_memories}"
)


# ============================================
# TEST 7 — EMOTION
# ============================================

print("\n")
print("TEST 7 — EMOTION")

emotion_result = analyze_message(
    "I am really nervous about my exam"
)

print(emotion_result)

emotion = emotion_result.get("emotion")

test(
    "Emotion analysis works",
    isinstance(emotion, dict)
)

test(
    "Nervous message detected as anxiety",
    emotion.get("emotion") == "anxiety",
    f"Detected emotion: {emotion}"
)


# ============================================
# TEST 8 — GENERAL MESSAGE
# ============================================

print("\n")
print("TEST 8 — GENERAL MESSAGE")

general_result = analyze_message(
    "The weather is nice today"
)

print(general_result)

general_cognition = general_result.get(
    "cognition",
    {}
)

test(
    "General message has general context",
    general_cognition.get("context") == "general",
    f"Detected context: {general_cognition.get('context')}"
)

test(
    "General message has no detected emotion",
    general_result.get("emotion") is None,
)


# ============================================
# TEST 9 — STATE OF MEMORY
# ============================================

print("\n")
print("TEST 9 — MEMORY INTEGRITY")

from core.memory import get_memory

memory = get_memory()

test(
    "Semantic memory still exists",
    len(memory["semantic"]["facts"]) == 3,
    f"Semantic memories: {memory['semantic']['facts']}"
)


# ============================================
# FINAL REPORT
# ============================================

print("\n")
print("=" * 70)
print("FINAL REPORT")
print("=" * 70)

passed = sum(results)
failed = len(results) - passed

print(f"\nTotal tests : {len(results)}")
print(f"Passed      : {passed}")
print(f"Failed      : {failed}")

if failed == 0:

    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                       ✅ ANALYZER PASS                              ║
║                                                                      ║
║  Cognition, emotion and memory recall work together correctly.      ║
╚══════════════════════════════════════════════════════════════════════╝
""")

else:

    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                       ❌ ANALYZER FAIL                              ║
║                                                                      ║
║  One or more Analyzer checks failed.                                ║
║  Inspect the output above.                                           ║
╚══════════════════════════════════════════════════════════════════════╝
""")