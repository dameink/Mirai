from datetime import datetime
from core.state_store import read_document, write_document
import uuid



class LearningSession:
    """
    Represents one complete learning session.

    Flow:

    Activity
        ↓
    Performance
        ↓
    Feedback
        ↓
    Result
        ↓
    History
    """



    def __init__(
        self,
        goal,
        mode,
        difficulty
    ):


        self.id = str(uuid.uuid4())


        self.created_at = datetime.now()


        self.goal = goal


        self.mode = mode


        self.difficulty = difficulty



        # Activity performed in session

        self.activity = None



        # User result

        self.result = {}
        self.message_count = 0



        # Detected mistakes

        self.mistakes = []



        # Improvements after session

        self.improvements = {}



        # Feedback messages

        self.feedback = []



        # Performance statistics

        self.performance = {


            "successes": 0,


            "mistakes": 0,


            "accuracy": 0

        }



        self.completed = False


        self.completed_at = None




    # =================================
    # Add activity
    # =================================


    def add_activity(
        self,
        activity
    ):


        self.activity = activity





    # =================================
    # Update performance
    # =================================


    def update_performance(
        self,
        success=False
    ):


        if success:

            self.performance["successes"] += 1


        else:

            self.performance["mistakes"] += 1



        total = (

            self.performance["successes"]

            +

            self.performance["mistakes"]

        )


        if total > 0:


            self.performance["accuracy"] = round(

                (

                    self.performance["successes"]

                    /

                    total

                )

                *

                100,

                2

            )





    # =================================
    # Add feedback
    # =================================


    def add_feedback(
        self,
        message
    ):


        self.feedback.append(
            message
        )


    # =================================
    # Save result
    # =================================

    def save_result(
        self,
        result,
        improvements,
        feedback=None,
        mistakes=None
    ):

        self.result = result

        self.improvements = improvements


        if feedback is not None:

            self.feedback = feedback

        if mistakes is not None:
            self.mistakes = mistakes




    # =================================
    # Summary
    # =================================


    def get_summary(self):
        return self.get_data()

    def get_data(self):
        return {
            "id": self.id,
            "message_count": self.message_count,
            "goal": self.goal,
            "mode": self.mode,
            "difficulty": self.difficulty,
            "activity": self.activity,
            "result": self.result,
            "mistakes": self.mistakes,
            "improvements": self.improvements,
            "performance": self.performance,
            "feedback": self.feedback,
            "completed": self.completed,
            "created_at": self.created_at,
            "completed_at": self.completed_at
        }

    def complete(
        self,
        result,
        improvements,
        mistakes=None
    ):

        self.result = result

        self.improvements = improvements

        values = []
        if result:
            values = [
                value
                for value in result.values()
                if isinstance(value, (int, float))
                ]

        if values:
            average = sum(values) / len(values)

            self.performance["accuracy"] = round(
                    average,
                    2
                )

            self.performance["successes"] = sum(
                    1 for value in values
                    if value >= 70
                )

            self.performance["mistakes"] = sum(
                    1 for value in values
                    if value < 70
                )

        if mistakes:
            self.mistakes = mistakes


        self.completed = True

        self.completed_at = datetime.now()






class SessionSystem:
    """
    Manages learning sessions and session history.
    """



    def __init__(
        self,
        learner
    ):


        self.learner = learner


        self.sessions = []
        self.user_id = learner.user_id
        if self.user_id:
            records = read_document(self.user_id, "learning_sessions", [])
            for record in records:
                session = LearningSession(record["goal"], record["mode"], record["difficulty"])
                for key in session.__dict__:
                    if key in record:
                        value = record[key]
                        if key in {"created_at", "completed_at"} and value:
                            value = datetime.fromisoformat(value)
                        setattr(session, key, value)
                self.sessions.append(session)

    def save(self):
        if self.user_id:
            records = []
            for session in self.sessions:
                record = session.get_data()
                for key in ("created_at", "completed_at"):
                    if record[key] is not None:
                        record[key] = record[key].isoformat()
                records.append(record)
            write_document(self.user_id, "learning_sessions", records)






    # =================================
    # Create session
    # =================================


    def create_session(
        self,
        goal,
        mode,
        difficulty
    ):


        session = LearningSession(

            goal,

            mode,

            difficulty

        )


        self.sessions.append(
            session
        )


        return session





    # =================================
    # Get current session
    # =================================


    def get_current_session(
        self
    ):


        if not self.sessions:

            return None


        return self.sessions[-1]





    # =================================
    # Complete current session
    # =================================


    def complete_current_session(
        self,
        result,
        mistakes=None,
        improvements=None
    ):
        session = self.get_current_session()

        if session:
            session.complete(
                result=result,
                improvements=improvements,
                mistakes=mistakes
            )

        self.save()
        return session





    # =================================
    # History
    # =================================


    def get_history(
        self
    ):


        return [


            session.get_summary()


            for session in self.sessions

        ]





    # =================================
    # Progress analysis
    # =================================


    def analyze_progress(
        self
    ):


        if len(self.sessions) < 2:

            return "not enough data"



        first = (

            self.sessions[0]

            .performance["accuracy"]

        )


        last = (

            self.sessions[-1]

            .performance["accuracy"]

        )



        difference = last - first



        if difference > 10:

            return "improving"



        elif difference < -10:

            return "declining"



        return "stable"
