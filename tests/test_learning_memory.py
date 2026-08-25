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



print("\n===== START LEARNING =====")


session = bridge.start_learning()


print(
    session.get_summary()
)



print("\n===== FIRST ANSWER WITH MISTAKES =====")


result_1 = {

    "fluency":75,

    "pronunciation":85,

    "grammar":40,

    "vocabulary":80

}


print(result_1)



print("\n===== PROCESS FIRST ANSWER =====")


response_1 = bridge.process_answer(
    result_1
)


print(response_1)



print("\n===== CHECK LEARNING MEMORY AFTER FIRST SESSION =====")


memory = learner.learning_memory


print(
    "Errors:"
)


print(
    memory.errors
)


print(
    "Sessions:"
)


print(
    memory.session_history
)



print("\n===== SECOND SESSION =====")


session_2 = bridge.start_learning()


print(
    session_2.get_summary()
)



print("\n===== SECOND ANSWER =====")


result_2 = {

    "fluency":85,

    "pronunciation":90,

    "grammar":75,

    "vocabulary":85

}


print(result_2)



print("\n===== PROCESS SECOND ANSWER =====")


response_2 = bridge.process_answer(
    result_2
)


print(response_2)



print("\n===== FINAL MEMORY =====")


print(
    "Errors:"
)


print(
    memory.errors
)


print(
    "\nCompleted topics:"
)


print(
    memory.completed_topics
)


print(
    "\nSuccessful methods:"
)


print(
    memory.successful_methods
)


print(
    "\nSession history:"
)


for session in memory.session_history:

    print(session)



print("\n===== TEST COMPLETED =====")