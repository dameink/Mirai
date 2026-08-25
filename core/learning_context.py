from core.learning_bridge import LearningBridge


class LearningContext:

    def __init__(
        self,
        bridge
    ):
        self.learning = bridge


    def get_context(self):

        return {

            "profile":
            self.learning.get_profile(),

            "strategy":
            self.learning.get_strategy(),

            "memory":
            self.learning.get_learning_memory(),

            "history":
            self.learning.get_history()

        }