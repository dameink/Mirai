from learning.learner import Learner
from learning.state import LearningState
from learning.difficulty import DifficultySystem
from learning.modes import ModeSystem



learner = Learner(
    native_language="Russian",
    learning_language="English"
)



learner.identity["level"] = "B2"



learner.update_motivation(
    "effort",
    90
)



learner.update_motivation(
    "engagement",
    90
)



state = LearningState(
    learner
)



mode = ModeSystem(
    learner
)



difficulty = DifficultySystem(

    learner,

    state,

    None,

    mode

)



print(
    difficulty.get_difficulty()
)