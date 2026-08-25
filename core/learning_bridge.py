from learning.controller import LearningController
from learning.influence import LearningInfluence
from learning.learning_events import detect_learning_event


class LearningBridge:
    """
    Connection layer between Mirai
    and Learning Engine.
    """

    def __init__(
        self,
        learner
    ):

        self.learning = LearningController(
            learner
        )

        self.influence = LearningInfluence(
            self.learning
        )


    # =========================
    # Start learning
    # =========================

    def start_learning(
        self
    ):
        return self.learning.start_session()



    # =========================
    # Analyze learner
    # =========================

    def analyze_user(
        self
    ):
        return self.learning.analyze()



    # =========================
    # Process user answer
    # =========================

    def process_answer(
        self,
        result
    ):
        return self.learning.complete_activity(
            result
        )



    # =========================
    # Process learning message
    # Main pipeline
    # =========================

    def process_message(
        self,
        message,
        context=None
    ):

        # Detect event
        event = detect_learning_event(
            message
        )


        # Update learner state
        if event:

            self.learning.update_from_event(
                event,
                message
            )


        # Generate learning strategy
        influence = self.influence.analyze(
            message,
            context,
            event
        )


        return {
            "event": event,
            "influence": influence,
            "profile": self.get_profile()
        }



    # =========================
    # Get learner profile
    # =========================

    def get_profile(
        self
    ):
        return self.learning.get_learning_profile()



    # =========================
    # Get strategy
    # =========================

    def get_strategy(
        self
    ):
        return self.learning.get_next_strategy()



    # =========================
    # Get session history
    # =========================

    def get_history(
        self
    ):
        return self.learning.sessions.get_history()



    # =========================
    # Learning memory
    # =========================

    def get_learning_memory(
        self
    ):
        return self.learning.get_memory()



    # =========================
    # Memory analysis
    # =========================

    def get_memory_analysis(
        self
    ):
        return (
            self.learning
            .get_memory_analysis()
        )



    # =========================
    # Get learning influence only
    # =========================

    def get_learning_influence(
        self,
        message,
        context=None
    ):

        event = detect_learning_event(
            message
        )


        return self.influence.analyze(
            message,
            context,
            event
        )