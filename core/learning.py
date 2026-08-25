from learning.learner import Learner
from core.learning_bridge import LearningBridge
from core.learning_context import LearningContext


learner = Learner(
    native_language="Russian",
    learning_language="English"
)


bridge = LearningBridge(
    learner
)


learning_context = LearningContext(
    bridge
)