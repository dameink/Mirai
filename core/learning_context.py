from core.learning_bridge import LearningBridge


class LearningContext:

    def __init__(self, bridge):
        self.learning = bridge
        self.last_result = {}

    def process_message(self, message, context=None):
        result = self.learning.process_message(
            message,
            context=context,
        )

        self.last_result = result or {}

        return self.last_result

    def get_context(self):

        result = self.last_result or {}

        return {

            "profile":
                result.get(
                    "profile",
                    self.learning.get_profile(),
                ),

            "strategy":
                result.get(
                    "strategy",
                    self.learning.get_strategy(),
                ),

            "memory":
                self.learning.get_learning_memory(),

            "history":
                self.learning.get_history(),

            "event":
                result.get(
                    "event"
                ),

            "influence":
                result.get(
                    "influence",
                    {},
                ),
        }