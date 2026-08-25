from learning.learner import Learner
from core.learning_bridge import LearningBridge


print("===== CREATE LEARNER =====")


learner = Learner(
    native_language="Russian",
    learning_language="English"
)


learner.set_goal(
    "ielts"
)


bridge = LearningBridge(
    learner
)



print("\n===== START SESSION =====")


session = bridge.start_learning()


print(
    session.get_summary()
)



print("\n===== FIRST ANSWER =====")


result = {

    "fluency": 75,

    "pronunciation": 85,

    "grammar": 40,

    "vocabulary": 80

}


print(result)



print("\n===== PROCESS ANSWER =====")


response = bridge.process_answer(
    result
)


print(response)



print("\n===== GET LEARNING MEMORY =====")


memory = bridge.get_learning_memory()



print("\nErrors:")

print(
    memory.errors
)



print("\nSession History:")

for session in memory.session_history:
    print(session)



print("\n===== TEST COMPLETED =====")