from learning.learner import Learner
from learning.strategy import LearningStrategy


learner = Learner(
    native_language="Russian",
    learning_language="English"
)


learner.identity["level"] = "B1"


strategy = LearningStrategy(
    learner
)


decision = {


    "focus": {

        "category": "grammar",

        "skill": "tenses"

    },


    "activity":
        "grammar explanation + exercises",


    "difficulty":
        "intermediate",


    "correction":
        "balanced correction",


    "goal":
        "improve tenses"

}



lesson = strategy.create_lesson(
    decision
)


print(lesson)