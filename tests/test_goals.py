from learning.controller import LearningController
from learning.learner import Learner


learner = Learner()

controller = LearningController(
    learner
)


print("\n===== BEFORE =====")
print(
    controller.get_goal_strategy()
)


message = "I want to prepare for IELTS speaking. My goal is band 8"


print("\n===== PROCESS MESSAGE =====")
goal = controller.process_goal(message)

print("Detected:", goal)


print("\n===== AFTER =====")
print(
    controller.get_goal_strategy()
)

print("\n===== PROCESS IELTS GOAL =====")

controller.process_goal(
    "I want to prepare for IELTS and get band 8"
)

print("\n===== ANALYSIS AFTER GOAL =====")

result = controller.analyze()

print(result["goal"])
print(result["activity"])