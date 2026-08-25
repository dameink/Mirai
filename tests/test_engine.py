from learning.learner import Learner
from learning.learning_engine import LearningEngine



learner = Learner(
    native_language="Russian",
    learning_language="English"
)


learner.set_goal(
    "ielts"
)


engine = LearningEngine(
    learner
)



print("\n===== START =====")

print(
    engine.learn()
)



print("\n===== RESULT =====")


result = {

    "fluency":75,

    "pronunciation":85,

    "grammar":60,

    "vocabulary":80

}


print(
    engine.learn(
        result
    )
)



print("\n===== PROFILE =====")


print(
    engine.get_profile()
)