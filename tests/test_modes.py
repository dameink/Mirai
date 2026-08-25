from learning.learner import Learner
from learning.modes import ModeSystem



# =====================================
# Test 1: New learner
# =====================================

print("\nTEST 1: Discovery mode")


learner = Learner(
    native_language="Russian",
    learning_language="English"
)


mode_system = ModeSystem(
    learner
)


print(
    mode_system.get_current_state()
)



# =====================================
# Test 2: Advanced motivated learner
# =====================================

print("\nTEST 2: Challenge mode")


learner = Learner(
    native_language="Russian",
    learning_language="English"
)


learner.identity["level"] = "C1"


learner.update_motivation(
    "engagement",
    90
)


learner.update_motivation(
    "effort",
    90
)


mode_system = ModeSystem(
    learner
)


print(
    mode_system.get_current_state()
)



# =====================================
# Test 3: Low confidence
# =====================================

print("\nTEST 3: Confidence mode")


learner = Learner(
    native_language="Russian",
    learning_language="English"
)


learner.identity["level"] = "B1"


learner.update_skill(
    "speaking",
    "confidence",
    10,
    50
)


learner.update_motivation(
    "engagement",
    80
)


learner.update_motivation(
    "effort",
    80
)


mode_system = ModeSystem(
    learner
)


print(
    mode_system.get_current_state()
)



# =====================================
# Test 4: Vocabulary weakness
# =====================================

print("\nTEST 4: Vocabulary mode")


learner = Learner(
    native_language="Russian",
    learning_language="English"
)


learner.identity["level"] = "B1"


learner.update_skill(
    "reading",
    "vocabulary",
    10,
    50
)


learner.update_motivation(
    "engagement",
    70
)


learner.update_motivation(
    "effort",
    70
)


mode_system = ModeSystem(
    learner
)


print(
    mode_system.get_current_state()
)