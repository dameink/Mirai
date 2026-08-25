from learning.learner import Learner
from core.learning_bridge import LearningBridge


print("===== CREATE LEARNER =====")

learner = Learner(
    native_language="Russian",
    learning_language="English"
)


bridge = LearningBridge(learner)


# ==================================
# FIRST SESSION
# ==================================

print("\n===== FIRST SESSION =====")

session = bridge.start_learning()

print(session.activity)


print("\n===== FIRST ANSWER (BAD GRAMMAR) =====")


answer1 = {
    "fluency": 75,
    "pronunciation": 85,
    "grammar": 40,
    "vocabulary": 80
}


result1 = bridge.process_answer(answer1)


print(result1)


# ==================================
# CHECK MEMORY
# ==================================

print("\n===== MEMORY =====")

from learning.memory_analysis import MemoryAnalysis

memory = bridge.get_learning_memory()

analysis = MemoryAnalysis(
    memory
)

print(
    analysis.get_analysis()
)


# ==================================
# CHECK ADAPTATION
# ==================================

print("\n===== FIRST STRATEGY =====")

strategy1 = bridge.get_strategy()

print(strategy1)



# ==================================
# SECOND SESSION
# ==================================

print("\n===== SECOND SESSION =====")

session = bridge.start_learning()

print(session.activity)



print("\n===== SECOND ANSWER (IMPROVED) =====")


answer2 = {
    "fluency": 85,
    "pronunciation": 90,
    "grammar": 75,
    "vocabulary": 85
}


result2 = bridge.process_answer(answer2)


print(result2)



# ==================================
# NEW STRATEGY
# ==================================

print("\n===== UPDATED STRATEGY =====")

strategy2 = bridge.get_strategy()

print(strategy2)



print("\n===== TEST COMPLETED =====")