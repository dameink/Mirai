from learning.learner import Learner
from learning.state import LearningState



learner = Learner(
    native_language="Russian",
    learning_language="English"
)



learner.identity["level"] = "B1"



learner.update_skill(
    "grammar",
    "tenses",
    20,
    60
)



state = LearningState(
    learner
)


print(
    state.get_state()
)