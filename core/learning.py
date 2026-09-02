from learning.learner import Learner
from core.learning_bridge import LearningBridge
from core.learning_context import LearningContext


def create_learning_context(user_id):
    learner = Learner(
        native_language="Russian",
        learning_language="English",
        user_id=user_id
    )

    bridge = LearningBridge(
        learner
    )

    return LearningContext(
        bridge
    )