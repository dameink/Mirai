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


class LearningController:
    """
    Main controller of Mirai Learning Engine.

    Flow:

    Analyze
        ↓
    Create session
        ↓
    Generate activity
        ↓
    User result
        ↓
    Evidence
        ↓
    Skill update
        ↓
    Save learning memory
        ↓
    Adaptation
        ↓
    Next activity
    """

    def __init__(
        self,
        learner
    ):

        self.learner = learner

        # =========================
        # Use learner memory
        # =========================

        self.memory = learner.learning_memory
        self.memory_analysis = MemoryAnalysis(
            self.memory
            )
        self.goal_detector = GoalDetector()


        # =========================
        # Analysis systems
        # =========================

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


        # =========================
        # Activity + Session
        # =========================

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


        # =========================
        # Learning loop
        # =========================

        self.feedback = FeedbackSystem(
            learner
        )

        self.mistakes = MistakeSystem(
            learner
        )

        self.updater = SkillUpdateSystem(
            learner
        )

        self.memory_analysis = MemoryAnalysis(
            self.memory
        )


        self.adaptation = Adaptation(
            learner,
            memory=self.memory,
            state=self.state
        )


    # =================================
    # Analyze learner
    # =================================

    def analyze(self):

        return {

            "state":
                self.state.get_state(),

            "goal":
                self.goals.get_goal_strategy(),

            "mode":
                self.modes.get_current_state(),

            "difficulty":
                self.difficulty.get_difficulty(),

            "activity":
                self.activities.generate_activity()
        }



    # =================================
    # Start learning session
    # =================================

    def start_session(
        self
    ):

        analysis = self.analyze()


        session = self.sessions.create_session(

            goal=
            analysis["goal"]["goal"],

            mode=
            analysis["mode"]["mode"],

            difficulty=
            analysis["difficulty"]["difficulty"]
        )


        session.add_activity(
            analysis["activity"]
        )


        return session

    def process_goal(self, message):
        goal = self.goal_detector.detect(message)

        if goal:
            self.goals.set_goal(goal)

        return goal

    # =================================
    # Get last session
    # =================================

    def get_last_session(
        self
    ):

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



    # =================================
    # Convert result to evidence
    # =================================

    def process_result(
        self,
        feedback_data
    ):

        evidences = []


        difficulty = (
            self.difficulty
            .get_difficulty()
            ["difficulty"]
        )


        for skill, value in feedback_data.items():


            category, real_skill = (
                self.detect_category(skill)
            )


            evidence = Evidence(

                skill=real_skill,

                category=category,

                value=value,

                evidence_type="performance",

                source="activity",

                certainty=70,

                context="activity",

                difficulty=difficulty
            )


            evidences.append(
                evidence
            )


        return (

            self.updater
            .update_from_evidence(
                evidences
            )
        )


# =========================
# Update learner from event
# =========================

    def update_from_event(
        self,
        event,
        message
    ):

        if event == "learning_goal":

            self.learner.set_goal(
                "conversation"
            )


        elif event == "learning_request":

            self.learner.update_preference(
                "preferred_activity",
                "conversation"
            )


        elif event == "ielts":

            self.learner.set_goal(
                "ielts"
            )


        elif event == "learning_progress":

            self.learner.update_skill(
                "speaking",
                "fluency",
                5,
                10
            )


        elif event == "learning_failure":

            current = self.learner.motivation[
                "engagement"
            ]

            self.learner.update_motivation(
                "engagement",
                current - 5
            )


        # Save event history

        self.learner.add_learning_event(
            event,
            message
        )
    # =================================
    # Complete activity
    # =================================

    def complete_activity(
        self,
        feedback_data
    ):


        session = self.get_last_session()

        if session is None:
            raise RuntimeError("No active learning lesson")

        if session.completed:
            raise RuntimeError("Session is already completed")


        activity = None


        if session:

            activity = session.activity



        feedback = self.feedback.analyze(

            activity,

            {
                "scores": feedback_data
            }
        )



        mistakes = (
            self.mistakes
            .process_feedback(
                feedback
            )
        )



        # =========================
        # Save mistakes to memory
        # =========================

        for mistake in mistakes:


            self.memory.add_error(

                skill=
                mistake["category"],

                mistake=
                mistake["description"]
            )



        # =========================
        # Save session history
        # =========================

        self.memory.add_session(

            {

                "activity":
                    activity["name"],


                "result":
                    feedback_data,


                "mistakes":

                    [
                        m["description"]
                        for m in mistakes
                    ],


                "scores":
                    feedback.scores
            }
        )



        # =========================
        # Update skills
        # =========================

        updates = self.process_result(

            feedback.scores
        )



        session = self.get_last_session()



        if session:


            session.save_result(

                result=
                feedback_data,


                improvements=
                updates,


                feedback=
                feedback.get_feedback(),


                mistakes=
                [
                    m["description"]
                    for m in mistakes
                ]
            )


            session.complete()

        strategy = self.get_next_strategy()

        self.learner.last_strategy = strategy
        self.learner.memory_storage.save(self.memory)

        return {


            "updates":

                updates,


            "mistakes":

                mistakes,


            "state":

                self.state.get_state(),


            "strategy":

                self.get_next_strategy(),


            "next_activity":

                self.activities.generate_activity()

        }



    # =================================
    # Skill mapping
    # =================================

    def detect_category(
        self,
        skill
    ):


        mapping = {


            "fluency":
                ("speaking", "fluency"),


            "pronunciation":
                ("speaking", "pronunciation"),


            "confidence":
                ("speaking", "confidence"),


            "accuracy":
                ("speaking", "accuracy"),


            "grammar":
                ("grammar", "tenses"),


            "tenses":
                ("grammar", "tenses"),


            "articles":
                ("grammar", "articles"),


            "word_order":
                ("grammar", "word_order"),


            "structure":
                ("writing", "structure"),


            "task_response":
                ("writing", "task_response"),


            "vocabulary":
                ("vocabulary", "range"),


            "collocations":
                ("vocabulary", "collocations"),


            "listening":
                ("listening", "general")

        }


        return mapping.get(

            skill,

            (
                "speaking",
                "fluency"
            )
        )



    # =================================
    # Adaptation
    # =================================

    def get_next_strategy(
        self
    ):

        return (

            self.adaptation
            .create_strategy()

        )



    # =================================
    # Profile
    # =================================

    def get_learning_profile(
        self
    ):


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



    # =================================
    # Memory access
    # =================================

    def get_memory(
        self
    ):

        return self.memory

    def get_goal_strategy(self):
        return self.goals.get_goal_strategy()

    def get_memory_analysis(
    self
    ):

        return (
            self.memory_analysis
            .get_analysis()
        )

    def add_learning_event(
        self,
        event,
        message
    ):

        self.history.append(
            {
                "event": event,
                "message": message
            }
        )