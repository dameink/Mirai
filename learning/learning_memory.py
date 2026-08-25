import os
import json


class LearningMemory:
    """
    Stores learning-related history.

    Responsible for:
    - mistakes
    - progress
    - topics
    - learning methods
    - learning patterns
    - sessions
    """


    def __init__(self):

        # mistakes history
        self.errors = []


        # completed learning materials
        self.completed_topics = []


        # topics learner struggles with
        self.difficult_topics = []


        # methods that work well
        self.successful_methods = []


        # learning behavior patterns
        self.patterns = []


        # skill improvement history
        self.skill_history = []


        # completed sessions
        self.session_history = []

        # learning goals history
        self.goal_history = []

        # learner preferences
        self.preferences = {}

        # important conversation events
        self.events = []

        # current learner identity
        self.identity = {
            "name": "",
            "native_language": "",
            "learning_language": "English",
            "level": "Unknown"
        }


        # current skills state
        self.skills = {}


        # learning statistics
        self.statistics = {
            "total_sessions": 0,
            "total_minutes": 0,
            "streak": 0
        }



    # =================================================
    # ERROR TRACKING
    # =================================================


    def add_error(
        self,
        skill,
        mistake,
        severity=50
    ):

        """
        Store learner mistake.

        If mistake already exists:
        increase frequency.
        """


        for error in self.errors:

            if (
                error["skill"] == skill
                and error["mistake"] == mistake
            ):

                error["frequency"] += 1

                error["severity"] = max(
                    error["severity"],
                    severity
                )

                return



        self.errors.append({

            "skill": skill,

            "mistake": mistake,

            "severity": severity,

            "frequency": 1

        })



    def get_common_errors(
        self,
        skill=None
    ):


        if skill:

            return [

                error

                for error in self.errors

                if error["skill"] == skill

            ]


        return self.errors



    # =================================================
    # SKILL PROGRESS
    # =================================================


    def add_skill_progress(
        self,
        skill,
        value,
        session_id=None
    ):


        self.skill_history.append({

            "skill": skill,

            "value": value,

            "session_id": session_id

        })



    def get_skill_history(
        self,
        skill
    ):


        return [

            item

            for item in self.skill_history

            if item["skill"] == skill

        ]



    # =================================================
    # TOPICS
    # =================================================


    def add_topic(
        self,
        topic
    ):


        if topic not in self.completed_topics:

            self.completed_topics.append(
                topic
            )



    def already_studied(
        self,
        topic
    ):


        return (

            topic

            in self.completed_topics

        )



    # =================================================
    # DIFFICULT TOPICS
    # =================================================


    def add_difficult_topic(
        self,
        topic
    ):


        if topic not in self.difficult_topics:

            self.difficult_topics.append(
                topic
            )



    def is_difficult(
        self,
        topic
    ):


        return (

            topic

            in self.difficult_topics

        )



    # =================================================
    # LEARNING METHODS
    # =================================================


    def add_successful_method(
        self,
        method
    ):


        if method not in self.successful_methods:

            self.successful_methods.append(
                method
            )



    def prefers_method(
        self,
        method
    ):


        return (

            method

            in self.successful_methods

        )



    # =================================================
    # LEARNING PATTERNS
    # =================================================


    def add_pattern(
        self,
        pattern,
        value=True
    ):


        self.patterns.append({

            "pattern": pattern,

            "value": value

        })



    def get_patterns(
        self
    ):


        return self.patterns



    # =================================================
    # SESSION HISTORY
    # =================================================


    def add_session(
        self,
        data
    ):


        self.session_history.append(
            data
        )



    def get_sessions(
        self
    ):


        return self.session_history


    # =================================================
    # GOAL MEMORY
    # =================================================

    def add_goal(
        self,
        goal
    ):
        """
        Save learner goal history.
        Example:
        IELTS -> conversation -> career
        """

        # prevent duplicate goals
        if self.goal_history:
            last_goal = self.goal_history[-1]["goal"]

            if last_goal == goal:
                return

        self.goal_history.append(
            {
                "goal": goal
            }
        )


    def get_goal_history(
        self
    ):
        return self.goal_history



    def get_last_goal(
        self
    ):
        if not self.goal_history:
            return None

        return self.goal_history[-1]["goal"]



    # =================================================
    # LEARNING PREFERENCES
    # =================================================

    def update_preference(
        self,
        key,
        value
    ):
        self.preferences[key] = value



    def get_preferences(
        self
    ):
        return self.preferences



    # =================================================
    # IMPORTANT EVENTS MEMORY
    # =================================================

    def add_event(
        self,
        event,
        data
    ):
        self.events.append(
            {
                "event": event,
                "data": data
            }
        )



    def get_events(
        self
    ):
        return self.events

    # =================================================
    # MEMORY SUMMARY
    # =================================================


    def get_memory_summary(self):

        return {

            "identity":
                self.identity,

            "skills":
                self.skills,

            "errors":
                self.errors,

            "completed_topics":
                self.completed_topics,

            "difficult_topics":
                self.difficult_topics,

            "successful_methods":
                self.successful_methods,

            "patterns":
                self.patterns,

            "skill_history":
                self.skill_history,

            "sessions":
                self.session_history,

            "goals":
                self.goal_history,

            "preferences":
                self.preferences,

            "events":
                self.events,

            "statistics":
                self.statistics
        }

    def get_weak_areas(self):

        areas = {}

        for error in self.errors:

            skill = error["skill"]

            if skill not in areas:

                areas[skill] = 0


            areas[skill] += error["frequency"]


        return areas

    def load_memory(self, data):

        self.errors = data.get(
            "errors",
            []
        )

        self.completed_topics = data.get(
            "completed_topics",
            []
        )

        self.difficult_topics = data.get(
            "difficult_topics",
            []
        )

        self.successful_methods = data.get(
            "successful_methods",
            []
        )

        self.patterns = data.get(
            "patterns",
            []
        )

        self.skill_history = data.get(
            "skill_history",
            []
        )

        self.session_history = data.get(
            "sessions",
            []
        )

        self.goal_history = data.get(
            "goals",
            []
        )

        self.preferences = data.get(
            "preferences",
            {}
        )

        self.events = data.get(
            "events",
            []
        )


        # NEW

        self.identity = data.get(
            "identity",
            {
                "name": "",
                "native_language": "",
                "learning_language": "English",
                "level": "Unknown"
            }
        )


        self.skills = data.get(
            "skills",
            {}
        )


        self.statistics = data.get(
            "statistics",
            {
                "total_sessions": 0,
                "total_minutes": 0,
                "streak": 0
            }
        )

        # =================================================
    # SAVE MEMORY
    # =================================================

    def save_memory(self, path="memory.json"):
        data = self.get_memory_summary()

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False,
                default=str
            )


    # =================================================
    # LOAD FROM FILE
    # =================================================


    def load_from_file(self, path="memory.json"):
        if not os.path.exists(path):
            return

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.load_memory(data)