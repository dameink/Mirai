from learning.learner import Learner
from core.learning_bridge import LearningBridge


print("===== CREATE LEARNER =====")


learner = Learner(
    native_language="Russian",
    learning_language="English"
)


bridge = LearningBridge(
    learner
)


print("\n===== START SESSION =====")


session = bridge.start_learning()


print(session)



print("\n===== ANSWER WITH MISTAKE =====")


answer = {

    "fluency": 75,

    "pronunciation": 85,

    "grammar": 40,

    "vocabulary": 80

}



print("\n===== PROCESS ANSWER =====")


result = bridge.process_answer(
    answer
)


print(result)



print("\n===== MEMORY ANALYSIS =====")


analysis = (
    bridge
    .get_memory_analysis()
)


print(analysis)



print("\n===== TEST COMPLETED =====")