from learning.learning_memory import LearningMemory
from learning.memory_analysis import MemoryAnalysis
from learning.adaptation import Adaptation
from learning.state import LearningState


class DummyLearner:

    def __init__(self):

        self.learning_memory = LearningMemory()

        self.goals = {
            "primary": "ielts",
            "secondary": []
        }

        self.skills = {
            "speaking": {
                "fluency": {
                    "value": 50,
                    "certainty": 50,
                    "evidence_count": 1,
                    "trend": 0
                },
                "accuracy": {
                    "value": 50,
                    "certainty": 50,
                    "evidence_count": 1,
                    "trend": 0
                }
            },
            "grammar": {
                "tenses": {
                    "value": 50,
                    "certainty": 50,
                    "evidence_count": 1,
                    "trend": 0
                },
                "articles": {
                    "value": 40,
                    "certainty": 50,
                    "evidence_count": 2,
                    "trend": -1
                }
            }
        }

        self.learning_preferences = {
            "prefers_explanations": True,
            "prefers_conversation": True,
            "likes_corrections": True,
            "correction_intensity": 50,
            "preferred_activity": None,
            "correction_preference": None
        }

    def get_skill(
        self,
        category,
        skill
    ):
        return (
            self.skills
            .get(category, {})
            .get(skill)
        )


learner = DummyLearner()


learner.learning_memory.add_error(
    "grammar",
    "articles"
)

learner.learning_memory.add_error(
    "grammar",
    "articles"
)


memory_analysis = MemoryAnalysis(
    learner.learning_memory
)


state = LearningState(
    learner
)


adaptation = Adaptation(
    learner,
    memory=memory_analysis,
    state=state
)


print(
    adaptation.create_strategy()
)