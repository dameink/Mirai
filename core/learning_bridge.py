
from learning.controller import LearningController
from learning.influence import LearningInfluence
from learning.learning_events import detect_learning_event


class LearningBridge:
    """
    Connection layer between Mirai and Learning Engine.

    Flow:

        User message
              ↓
        LearningController
              ↓
        ConversationAssessment
              ↓
        SkillUpdateSystem
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
                "strategy": self.get_strategy(),
                "learning_result": {}
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
                "strategy": self.get_strategy(),
                "learning_result": {}
            }

        # =========================
        # Detect learning event
        # =========================

        event = detect_learning_event(
            message
        )

        # =========================
        # Update learner from event
        # =========================

        if event:

            self.learning.update_from_event(
                event,
                message
            )

        # =========================
        # IMPORTANT:
        # Process EVERY user message
        # through the Learning Engine.
        #
        # This runs:
        # ConversationAssessment
        #        ↓
        # Evidence
        #        ↓
        # SkillUpdateSystem
        #        ↓
        # Save memory
        # =========================

        learning_result = self.learning.process_message(
            message,
            context=context
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

            "profile": profile,

            "learning_result": learning_result
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
