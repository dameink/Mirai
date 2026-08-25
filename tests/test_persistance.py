from learning.learner import Learner
from learning.controller import LearningController


print("=" * 60)
print("MIRAI FULL BACKEND PERSISTENCE TEST")
print("=" * 60)


# ============================================================
# FIRST RUN
# ============================================================

print("\n===== FIRST RUN =====")

learner = Learner(
    native_language="Russian",
    learning_language="English"
)

controller = LearningController(learner)

# Set goal
learner.set_goal("ielts")

# Create some real skill data
learner.update_skill(
    "speaking",
    "fluency",
    50,
    70
)

learner.update_skill(
    "grammar",
    "articles",
    40,
    60
)

# Add learning history
learner.learning_memory.add_error(
    skill="grammar",
    mistake="articles",
    severity=80
)

learner.learning_memory.add_session({
    "activity": "IELTS Speaking Part 2",
    "score": 75
})

learner.learning_memory.add_event(
    "learning_goal",
    "Prepare for IELTS"
)

# Save everything
learner.memory_storage.save(
    learner.learning_memory
)

print("\n--- BEFORE RESTART ---")

print("Goal:")
print(learner.goals)

print("\nSpeaking fluency:")
print(
    learner.get_skill(
        "speaking",
        "fluency"
    )
)

print("\nGrammar articles:")
print(
    learner.get_skill(
        "grammar",
        "articles"
    )
)

print("\nMemory:")
print(
    learner.learning_memory.get_memory_summary()
)


# ============================================================
# SECOND RUN
# ============================================================

print("\n\n===== SECOND RUN =====")

# Create completely new Learner.
# This simulates restarting the application.
learner2 = Learner(
    native_language="Russian",
    learning_language="English"
)

controller2 = LearningController(learner2)


print("\n--- AFTER RESTART ---")

print("Goal:")
print(learner2.goals)

print("\nSpeaking fluency:")
print(
    learner2.get_skill(
        "speaking",
        "fluency"
    )
)

print("\nGrammar articles:")
print(
    learner2.get_skill(
        "grammar",
        "articles"
    )
)

print("\nMemory:")
print(
    learner2.learning_memory.get_memory_summary()
)


# ============================================================
# CHECK
# ============================================================

print("\n\n===== CHECK =====")

memory = learner2.learning_memory.get_memory_summary()

# Goal
goal_ok = (
    learner2.learning_memory.get_last_goal()
    == "ielts"
)

# Error
errors_ok = any(
    error["skill"] == "grammar"
    and error["mistake"] == "articles"
    for error in memory["errors"]
)

# Session
sessions_ok = any(
    session["activity"]
    == "IELTS Speaking Part 2"
    for session in memory["sessions"]
)

# Event
events_ok = any(
    event["event"] == "learning_goal"
    for event in memory["events"]
)

# Speaking skill
speaking = learner2.get_skill(
    "speaking",
    "fluency"
)

speaking_ok = (
    speaking["value"] == 50
    and speaking["evidence_count"] == 1
)

# Grammar skill
grammar = learner2.get_skill(
    "grammar",
    "articles"
)

grammar_ok = (
    grammar["value"] == 40
    and grammar["evidence_count"] == 1
)


print(
    "Goals:",
    "✅" if goal_ok else "❌"
)

print(
    "Errors:",
    "✅" if errors_ok else "❌"
)

print(
    "Sessions:",
    "✅" if sessions_ok else "❌"
)

print(
    "Events:",
    "✅" if events_ok else "❌"
)

print(
    "Speaking skill:",
    "✅" if speaking_ok else "❌"
)

print(
    "Grammar skill:",
    "✅" if grammar_ok else "❌"
)


# ============================================================
# FINAL RESULT
# ============================================================

all_ok = (
    goal_ok
    and errors_ok
    and sessions_ok
    and events_ok
    and speaking_ok
    and grammar_ok
)

print("\n" + "=" * 60)

if all_ok:
    print("✅ FULL BACKEND PERSISTENCE TEST PASSED")
    print("✅ LEARNING STATE SURVIVES RESTART")
else:
    print("❌ FULL BACKEND PERSISTENCE TEST FAILED")
    print("Check the failed component above.")

print("=" * 60)