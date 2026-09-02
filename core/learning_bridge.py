from learning.controller import LearningController
from learning.influence import LearningInfluence
from learning.learning_events import detect_learning_event


class LearningBridge:
    """
    Connection layer between Mirai and Learning Engine.

    Flow:

        User message
              ↓
        detect learning event
              ↓
        LearningController
              ↓
        LearningInfluence
              ↓
        learning result
              ↓
        Main Mirai pipeline

    This layer does NOT use an LLM.
    """

    def __init__(self, learner):

        self.learner = learner

        # =========================
        # Learning engine
        # =========================

        self.learning = LearningController(
            learner
        )

        # =========================
        # Learning influence
        # =========================

        self.influence = LearningInfluence(
            self.learning
        )

    # =========================================================
    # START LEARNING
    # =========================================================

    def start_learning(self):

        return self.learning.start_session()

    # =========================================================
    # ANALYZE LEARNER
    # =========================================================

    def analyze_user(self):

        return self.learning.analyze()

    # =========================================================
    # PROCESS USER ANSWER
    # =========================================================

    def process_answer(self, result):

        return self.learning.complete_activity(
            result
        )

    # =========================================================
    # PROCESS USER MESSAGE
    #
    # This is the main connection between
    # conversation and learning.
    # =========================================================

    def process_message(
        self,
        message,
        context=None
    ):

        context = context or {}

        # =========================
        # Safety
        # =========================

        if not message:

            return {
                "event": None,
                "influence": {
                    "should_teach": False,
                    "focus": None,
                    "activity": None,
                    "strategy": None,
                    "intensity": 0,
                    "reason": None
                },
                "profile": self.get_profile(),
                "strategy": self.get_strategy()
            }

        message = str(message).strip()

        if not message:

            return {
                "event": None,
                "influence": {
                    "should_teach": False,
                    "focus": None,
                    "activity": None,
                    "strategy": None,
                    "intensity": 0,
                    "reason": None
                },
                "profile": self.get_profile(),
                "strategy": self.get_strategy()
            }

        # =========================
        # Detect learning event
        # =========================

        event = detect_learning_event(
            message
        )

        # =========================
        # Update learner
        # =========================

        if event:

            self.learning.update_from_event(
                event,
                message
            )

        # =========================
        # Analyze learning influence
        # =========================

        influence = self.influence.analyze(
            message,
            context,
            event
        )

        # =========================
        # Current strategy
        # =========================

        strategy = self.get_strategy()

        # =========================
        # Current profile
        # =========================

        profile = self.get_profile()

        # =========================
        # Return everything
        # =========================

        return {

            "event": event,

            "influence": influence,

            "strategy": strategy,

            "profile": profile
        }

    # =========================================================
    # GET LEARNER PROFILE
    # =========================================================

    def get_profile(self):

        return self.learning.get_learning_profile()

    # =========================================================
    # GET CURRENT LEARNING STRATEGY
    # =========================================================

    def get_strategy(self):

        return self.learning.get_next_strategy()

    # =========================================================
    # GET SESSION HISTORY
    # =========================================================

    def get_history(self):

        return self.learning.sessions.get_history()

    # =========================================================
    # GET LEARNING MEMORY
    # =========================================================

    def get_learning_memory(self):

        return self.learning.get_memory()

    # =========================================================
    # GET MEMORY ANALYSIS
    # =========================================================

    def get_memory_analysis(self):

        return self.learning.get_memory_analysis()

    # =========================================================
    # GET LEARNING INFLUENCE ONLY
    # =========================================================

    def get_learning_influence(
        self,
        message,
        context=None
    ):

        context = context or {}

        event = detect_learning_event(
            message
        )

        return self.influence.analyze(
            message,
            context,
            event
        )

    # =========================================================
    # GET CURRENT LEARNING STATE
    # =========================================================

    def get_state(self):

        return self.learning.state.get_state()

    # =========================================================
    # GET CURRENT GOAL
    # =========================================================

    def get_goal(self):

        return self.learning.get_goal_strategy()

    # =========================================================
    # GET ACTIVE SESSION
    # =========================================================

    def get_active_session(self):

        return self.learning.get_last_session()

    # =========================================================
    # CHECK WHETHER LEARNING SHOULD HAPPEN
    # =========================================================

    def should_teach(
        self,
        message,
        context=None
    ):

        influence = self.get_learning_influence(
            message,
            context
        )

        return influence.get(
            "should_teach",
            False
        )

    # =========================================================
    # GET NEXT ACTIVITY
    # =========================================================

    def get_next_activity(self):

        analysis = self.learning.analyze()

        return analysis.get(
            "activity"
        )

    # =========================================================
    # COMPLETE CURRENT ACTIVITY
    # =========================================================

    def complete_learning(
        self,
        result
    ):

        return self.learning.complete_activity(
            result
        )