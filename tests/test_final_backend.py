from learning.learner import Learner


def check(name, condition):
    mark = "✅" if condition else "❌"
    print(f"{name}: {mark}")
    return condition


print("=" * 60)
print("MIRAI FULL BACKEND PERSISTENCE TEST")
print("=" * 60)


# =================================================
# FIRST RUN
# =================================================

print("\n===== FIRST RUN =====")

learner = Learner(
    native_language="Russian",
    learning_language="English"
)

# Goal
learner.set_goal("ielts")

# Skills
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

# Memory data
learner.learning_memory.add_error(
    skill="grammar",
    mistake="articles",
    severity=80
)

learner.learning_memory.add_session(
    {
        "activity": "IELTS Speaking Part 2",
        "score": 75
    }
)

learner.add_learning_event(
    "learning_goal",
    "Prepare for IELTS"
)

# Save ONLY through MemoryStorage → learner.json
learner.memory_storage.save(
    learner.learning_memory
)

print("\n--- BEFORE RESTART ---")
print("Goal:", learner.goals)
print("Speaking fluency:", learner.get_skill("speaking", "fluency"))
print("Grammar articles:", learner.get_skill("grammar", "articles"))


# =================================================
# SECOND RUN
# =================================================

print("\n===== SECOND RUN =====")

# Learner loads learner.json automatically in __init__.
# Do NOT call load_from_file().
new_learner = Learner(
    native_language="Russian",
    learning_language="English"
)

restored_goal = new_learner.goals["primary"]
restored_speaking = new_learner.get_skill("speaking", "fluency")
restored_grammar = new_learner.get_skill("grammar", "articles")
memory = new_learner.learning_memory.get_memory_summary()

print("\n--- AFTER RESTART ---")
print("Goal:", new_learner.goals)
print("Speaking fluency:", restored_speaking)
print("Grammar articles:", restored_grammar)


# =================================================
# CHECK
# =================================================

print("\n===== CHECK =====")

results = [
    check("Goals", restored_goal == "ielts"),
    check("Errors", len(memory["errors"]) > 0),
    check("Sessions", len(memory["sessions"]) > 0),
    check("Events", len(memory["events"]) > 0),
    check(
        "Speaking skill",
        restored_speaking["value"] == 50
        and restored_speaking["evidence_count"] == 1
    ),
    check(
        "Grammar skill",
        restored_grammar["value"] == 40
        and restored_grammar["evidence_count"] == 1
    )
]

print("\n" + "=" * 60)

if all(results):
    print("✅ FULL BACKEND PERSISTENCE TEST PASSED")
    print("✅ LEARNING STATE SURVIVES RESTART")
else:
    print("❌ FULL BACKEND PERSISTENCE TEST FAILED")

print("=" * 60)