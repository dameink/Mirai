from learning.learner import Learner
from learning.controller import LearningController



learner = Learner(

    native_language="Russian",

    learning_language="English"

)



# Simulate learner

learner.identity["level"] = "B1"



learner.set_goal(

    primary="ielts"

)



learner.update_motivation(
    "effort",
    80
)


learner.update_motivation(
    "engagement",
    85
)



controller = LearningController(
    learner
)



print("\nANALYSIS")

print(
    controller.analyze()
)



print("\nSESSION")

session = controller.start_session()


print(
    session.get_summary()
)



print("\nPROFILE")

print(
    controller.get_learning_profile()
)