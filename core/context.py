class MiraiContext:

    def __init__(
        self,
        core,
        learning
    ):
        self.core = core
        self.learning = learning


    def build(self):

        return {

            "personality":
                self.core.get_personality(),

            "emotion":
                self.core.get_emotion(),

            "memory":
                self.core.get_memory(),

            "learning":
                self.learning.get_learning_profile(),

            "strategy":
                self.learning.get_strategy()

        }