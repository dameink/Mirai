from learning.state import LearningState
from learning.goals import GoalSystem
from learning.modes import ModeSystem
from learning.difficulty import DifficultySystem
from learning.session import SessionSystem
from learning.activity import ActivitySystem
from learning.mistake import MistakeSystem
from learning.update import SkillUpdateSystem
from learning.evidence import Evidence
from learning.feedback import FeedbackSystem
from learning.adaptation import Adaptation
from learning.memory_analysis import MemoryAnalysis
from learning.goal_detector import GoalDetector
from learning.learning_events import (
    detect_learning_event,
    detect_learning_goal
)


class LearningController:
    """
    Main controller of Mirai Learning Engine.

    Main flow:

        Analyze
            ↓
        Create session
            ↓
        Generate activity
            ↓
        User result
            ↓
        Feedback
            ↓
        Mistakes
            ↓
        Evidence
            ↓
        Skill update
            ↓
        Save memory
            ↓
        Adaptation
            ↓
        Next activity
    """

    def __init__(self, learner):

        self.learner = learner

        # =================================================
        # MEMORY
        # =================================================

        self.memory = learner.learning_memory

        self.memory_analysis = MemoryAnalysis(
            self.memory
        )

        # =================================================
        # GOAL DETECTION
        # =================================================

        self.goal_detector = GoalDetector()

        # =================================================
        # ANALYSIS SYSTEMS
        # =================================================

        self.state = LearningState(
            learner
        )

        self.goals = GoalSystem(
            learner
        )

        self.modes = ModeSystem(
            learner,
            self.goals
        )

        self.difficulty = DifficultySystem(
            learner,
            self.state,
            self.goals,
            self.modes
        )

        # =================================================
        # ACTIVITY + SESSION
        # =================================================

        self.activities = ActivitySystem(
            learner,
            self.state,
            self.goals,
            self.modes,
            self.difficulty
        )

        self.sessions = SessionSystem(
            learner
        )

        # =================================================
        # LEARNING LOOP
        # =================================================

        self.feedback = FeedbackSystem(
            learner
        )

        self.mistakes = MistakeSystem(
            learner
        )

        self.updater = SkillUpdateSystem(
            learner
        )

        self.adaptation = Adaptation(
            learner,
            memory=self.memory,
            state=self.state
        )

    # =====================================================
    # ANALYZE LEARNER
    # =====================================================

    def analyze(self):
        """
        Analyze the current learner state and determine:

        - current state
        - goal
        - learning mode
        - difficulty
        - next activity
        """

        return {
            "state": self.state.get_state(),

            "goal": self.goals.get_goal_strategy(),

            "mode": self.modes.get_current_state(),

            "difficulty": self.difficulty.get_difficulty(),

            "activity": self.activities.generate_activity()
        }

    # =====================================================
    # START LEARNING SESSION
    # =====================================================

    def start_session(self):
        """
        Create a new learning session based on
        the current learner analysis.
        """

        analysis = self.analyze()

        goal_data = analysis["goal"]
        mode_data = analysis["mode"]
        difficulty_data = analysis["difficulty"]

        goal = (
            goal_data.get("goal")
            if isinstance(goal_data, dict)
            else goal_data
        )

        mode = (
            mode_data.get("mode")
            if isinstance(mode_data, dict)
            else mode_data
        )

        difficulty = (
            difficulty_data.get("difficulty")
            if isinstance(difficulty_data, dict)
            else difficulty_data
        )

        session = self.sessions.create_session(
            goal=goal,
            mode=mode,
            difficulty=difficulty
        )

        activity = analysis["activity"]

        if activity:
            session.add_activity(
                activity
            )

        return session

    # =====================================================
    # PROCESS GOAL
    # =====================================================

    def process_goal(self, message):
        """
        Detect a learning goal from the user's message.

        The detected goal is passed to GoalSystem.
        """

        if not message:
            return None

        goal = None

        # -------------------------------------------------
        # First try GoalDetector
        # -------------------------------------------------

        if hasattr(self.goal_detector, "detect"):

            try:
                goal = self.goal_detector.detect(
                    message
                )
            except Exception:
                goal = None

        # -------------------------------------------------
        # Fallback to learning_events detector
        # -------------------------------------------------

        if goal is None:

            try:
                goal = detect_learning_goal(
                    message
                )
            except Exception:
                goal = None

        # -------------------------------------------------
        # Save goal
        # -------------------------------------------------

        if goal:

            if hasattr(self.goals, "set_goal"):

                self.goals.set_goal(
                    goal
                )

            elif hasattr(
                self.learner,
                "set_goal"
            ):

                self.learner.set_goal(
                    goal
                )

        return goal

    # =====================================================
    # PROCESS LEARNING EVENT
    # =====================================================

    def process_learning_event(self, message):
        """
        Detect and process a learning-related event
        from the user's message.

        Returns the detected event.
        """

        if not message:
            return None

        event = detect_learning_event(
            message
        )

        if event:
            self.update_from_event(
                event,
                message
            )

        return event

    # =====================================================
    # PROCESS MESSAGE
    # =====================================================

    def process_message(self, message):
        """
        Main entry point for learning-related user messages.

        Detects:

        - learning goal
        - learning request
        - exam preparation
        - learning progress
        - learning failure
        - other learning events
        """

        if not message:
            return {
                "event": None,
                "goal": None
            }

        goal = self.process_goal(
            message
        )

        event = self.process_learning_event(
            message
        )

        return {
            "event": event,
            "goal": goal
        }

    # =====================================================
    # GET LAST SESSION
    # =====================================================

    def get_last_session(self):

        if hasattr(
            self.sessions,
            "get_last_session"
        ):

            return self.sessions.get_last_session()

        if hasattr(
            self.sessions,
            "sessions"
        ):

            if not self.sessions.sessions:
                return None

            return self.sessions.sessions[-1]

        return None

    # =====================================================
    # CONVERT RESULT TO EVIDENCE
    # =====================================================

    def process_result(self, feedback_data):
        """
        Convert performance scores into Evidence objects
        and update learner skills.
        """

        if not feedback_data:
            return {}

        evidences = []

        difficulty_data = (
            self.difficulty.get_difficulty()
        )

        if isinstance(
            difficulty_data,
            dict
        ):
            difficulty = difficulty_data.get(
                "difficulty"
            )
        else:
            difficulty = difficulty_data

        for skill, value in feedback_data.items():

            # Ignore non-numeric values
            if not isinstance(
                value,
                (int, float)
            ):
                continue

            category, real_skill = (
                self.detect_category(skill)
            )

            # Unknown skill
            if not category or not real_skill:
                continue

            # Never allow category/category
            if category == real_skill:
                continue

            evidence = Evidence(
                skill=real_skill,
                category=category,
                value=value,
                topic=skill,
                evidence_type="performance",
                source="activity",
                certainty=70,
                context="activity",
                difficulty=difficulty
            )

            evidences.append(
                evidence
            )

        if not evidences:
            return {}

        return self.updater.update_from_evidence(
            evidences
        )

    # =====================================================
    # UPDATE LEARNER FROM EVENT
    # =====================================================

    def update_from_event(
        self,
        event,
        message
    ):
        """
        Apply the detected learning event
        to the learner profile.
        """

        if event == "learning_goal":

            goal = None

            try:
                goal = detect_learning_goal(
                    message
                )
            except Exception:
                pass

            if goal:

                if hasattr(
                    self.goals,
                    "set_goal"
                ):

                    self.goals.set_goal(
                        goal
                    )

                else:

                    self.learner.set_goal(
                        goal
                    )

        elif event == "learning_request":

            self.learner.update_preference(
                "preferred_activity",
                "conversation"
            )

            self.learner.learning_preferences[
                "prefers_conversation"
            ] = True

        elif event == "exam_preparation":

            goal = None

            try:
                goal = detect_learning_goal(
                    message
                )
            except Exception:
                pass

            if goal:

                if hasattr(
                    self.goals,
                    "set_goal"
                ):

                    self.goals.set_goal(
                        goal
                    )

                else:

                    self.learner.set_goal(
                        goal
                    )

        elif event == "learning_progress":

            self.learner.update_skill(
                "speaking",
                "fluency",
                5,
                10
            )

        elif event == "learning_failure":

            current = self.learner.motivation.get(
                "engagement",
                50
            )

            self.learner.update_motivation(
                "engagement",
                current - 5
            )

        # -------------------------------------------------
        # Save event to learning memory
        # -------------------------------------------------

        self.learner.add_learning_event(
            event,
            message
        )

    # =====================================================
    # COMPLETE ACTIVITY
    # =====================================================

    def complete_activity(
        self,
        feedback_data
    ):
        """
        Complete the current activity.

        Flow:

        result
            ↓
        feedback
            ↓
        mistakes
            ↓
        memory
            ↓
        evidence
            ↓
        skill update
            ↓
        adaptation
            ↓
        next activity
        """

        session = self.get_last_session()

        if session is None:
            raise RuntimeError(
                "No active learning lesson"
            )

        if getattr(
            session,
            "completed",
            False
        ):
            raise RuntimeError(
                "Session is already completed"
            )

        activity = getattr(
            session,
            "activity",
            None
        )

        if activity is None:
            raise RuntimeError(
                "Session has no activity"
            )

        # =================================================
        # FEEDBACK
        # =================================================

        feedback = self.feedback.analyze(
            activity,
            {
                "scores": feedback_data
            }
        )

        # =================================================
        # MISTAKES
        # =================================================

        mistakes = self.mistakes.process_feedback(
            feedback
        )

        if mistakes is None:
            mistakes = []

        # =================================================
        # SAVE MISTAKES TO MEMORY
        # =================================================

        for mistake in mistakes:

            if not isinstance(
                mistake,
                dict
            ):
                continue

            category = mistake.get(
                "category",
                "unknown"
            )

            description = mistake.get(
                "description",
                ""
            )

            if description:

                self.memory.add_error(
                    skill=category,
                    mistake=description
                )

        # =================================================
        # FEEDBACK SCORES
        # =================================================

        scores = getattr(
            feedback,
            "scores",
            feedback_data
        )

        # =================================================
        # SAVE SESSION TO MEMORY
        # =================================================

        self.memory.add_session(
            {
                "activity": activity.get(
                    "name",
                    "unknown"
                ),

                "result": feedback_data,

                "mistakes": [
                    m.get(
                        "description",
                        ""
                    )
                    for m in mistakes
                    if isinstance(m, dict)
                ],

                "scores": scores
            }
        )

        # =================================================
        # UPDATE SKILLS
        # =================================================

        updates = self.process_result(
            scores
        )

        # =================================================
        # SESSION RESULT
        # =================================================

        mistake_descriptions = [
            m.get(
                "description",
                ""
            )
            for m in mistakes
            if isinstance(m, dict)
        ]

        if hasattr(
            session,
            "save_result"
        ):

            session.save_result(
                result=feedback_data,
                improvements=updates,
                feedback=feedback.get_feedback(),
                mistakes=mistake_descriptions
            )

        # =================================================
        # PERFORMANCE
        # =================================================

        numeric_values = [
            value
            for value in feedback_data.values()
            if isinstance(
                value,
                (int, float)
            )
        ]

        successes = sum(
            1
            for value in numeric_values
            if value >= 70
        )

        failures = sum(
            1
            for value in numeric_values
            if value < 70
        )

        accuracy = (
            round(
                sum(numeric_values)
                / len(numeric_values),
                2
            )
            if numeric_values
            else 0
        )

        session.performance = {
            "successes": successes,
            "mistakes": failures,
            "accuracy": accuracy
        }

        # =================================================
        # COMPLETE SESSION
        # =================================================

        session.complete(
            result=feedback_data,
            improvements=updates,
            mistakes=mistake_descriptions
        )

        # =================================================
        # ADAPTATION
        # =================================================

        strategy = self.get_next_strategy()

        self.learner.last_strategy = strategy

        # =================================================
        # SAVE MEMORY
        # =================================================

        self.learner.memory_storage.save(
            self.memory
        )

        # =================================================
        # NEXT ACTIVITY
        # =================================================

        next_activity = (
            self.activities.generate_activity()
        )

        return {
            "updates": updates,

            "mistakes": mistakes,

            "state": self.state.get_state(),

            "strategy": strategy,

            "next_activity": next_activity
        }

    # =====================================================
    # SKILL MAPPING
    # =====================================================

    def detect_category(
        self,
        skill
    ):
        """
        Convert a skill name into:

            category + real skill

        Categories themselves are never treated
        as individual skills.
        """

        if not isinstance(
            skill,
            str
        ):
            return None, None

        skill = skill.lower().strip()

        mapping = {

            # -------------------------
            # Speaking
            # -------------------------

            "fluency": (
                "speaking",
                "fluency"
            ),

            "pronunciation": (
                "speaking",
                "pronunciation"
            ),

            "confidence": (
                "speaking",
                "confidence"
            ),

            "accuracy": (
                "speaking",
                "accuracy"
            ),

            # -------------------------
            # Grammar
            # -------------------------

            "grammar": (
                "grammar",
                "tenses"
            ),

            "tenses": (
                "grammar",
                "tenses"
            ),

            "articles": (
                "grammar",
                "articles"
            ),

            "word_order": (
                "grammar",
                "word_order"
            ),

            # -------------------------
            # Writing
            # -------------------------

            "structure": (
                "writing",
                "structure"
            ),

            "task_response": (
                "writing",
                "task_response"
            ),

            # -------------------------
            # Vocabulary
            # -------------------------

            "vocabulary": (
                "vocabulary",
                "range"
            ),

            "range": (
                "vocabulary",
                "range"
            ),

            "collocations": (
                "vocabulary",
                "collocations"
            ),

            # -------------------------
            # Listening
            # -------------------------

            "listening": (
                "listening",
                "general"
            ),

            "general": (
                "listening",
                "general"
            ),

            "native_speed": (
                "listening",
                "native_speed"
            ),

            # -------------------------
            # Reading
            # -------------------------

            "reading": (
                "reading",
                "comprehension"
            ),

            "comprehension": (
                "reading",
                "comprehension"
            )
        }

        return mapping.get(
            skill,
            (None, None)
        )

    # =====================================================
    # NEXT STRATEGY
    # =====================================================

    def get_next_strategy(self):

        return self.adaptation.create_strategy()

    # =====================================================
    # LEARNING PROFILE
    # =====================================================

    def get_learning_profile(self):

        return {
            "learner":
                self.learner.get_profile(),

            "analysis":
                self.analyze(),

            "strategy":
                self.get_next_strategy(),

            "sessions":
                self.sessions.get_history()
        }

    # =====================================================
    # MEMORY
    # =====================================================

    def get_memory(self):

        return self.memory

    # =====================================================
    # GOAL STRATEGY
    # =====================================================

    def get_goal_strategy(self):

        return self.goals.get_goal_strategy()

    # =====================================================
    # MEMORY ANALYSIS
    # =====================================================

    def get_memory_analysis(self):

        return self.memory_analysis.get_analysis()

    # =====================================================
    # LEARNING EVENT
    # =====================================================

    def add_learning_event(
        self,
        event,
        message
    ):
        """
        Compatibility method.

        Learning history itself belongs to Learner,
        so delegate the event there.
        """

        self.learner.add_learning_event(
            event,
            message
        )