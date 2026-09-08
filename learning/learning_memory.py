
import os
import json


class LearningMemory:
    """
    Persistent learning-related memory.

    Stores:
    - learner identity
    - current goals
    - goal history
    - motivation
    - skills
    - skill progress
    - mistakes
    - topics
    - learning methods
    - learning patterns
    - sessions
    - activity history
    - preferences
    - important events
    - statistics
    """

    def __init__(self):

        # =================================================
        # ERROR HISTORY
        # =================================================

        self.errors = []

        # =================================================
        # TOPICS
        # =================================================

        self.completed_topics = []
        self.difficult_topics = []

        # =================================================
        # LEARNING METHODS
        # =================================================

        self.successful_methods = []

        # =================================================
        # LEARNING PATTERNS
        # =================================================

        self.patterns = []

        # =================================================
        # SKILLS
        # =================================================

        self.skills = {}

        # =================================================
        # SKILL PROGRESS HISTORY
        # =================================================

        self.skill_history = []

        # =================================================
        # SESSION HISTORY
        # =================================================

        self.session_history = []

        # =================================================
        # GENERAL ACTIVITY HISTORY
        # =================================================

        self.history = []

        # =================================================
        # GOALS
        # =================================================

        # Historical goals
        self.goal_history = []

        # Current goals
        self.goals = {
            "primary": None,
            "secondary": []
        }

        # =================================================
        # MOTIVATION
        # =================================================

        self.motivation = {
            "consistency": 50,
            "effort": 50,
            "engagement": 50
        }

        # =================================================
        # LEARNER PREFERENCES
        # =================================================

        self.preferences = {}

        # =================================================
        # IMPORTANT EVENTS
        # =================================================

        self.events = []

        # =================================================
        # LEARNER IDENTITY
        # =================================================

        self.identity = {
            "name": "",
            "native_language": "",
            "learning_language": "English",
            "level": "Unknown"
        }

        # =================================================
        # STATISTICS
        # =================================================

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

        If the same mistake already exists,
        increase its frequency.
        """

        for error in self.errors:

            if (
                error.get("skill") == skill
                and error.get("mistake") == mistake
            ):

                error["frequency"] = (
                    error.get("frequency", 0) + 1
                )

                error["severity"] = max(
                    error.get("severity", 0),
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
                if error.get("skill") == skill
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
            if item.get("skill") == skill
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

        return topic in self.completed_topics

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

        return topic in self.difficult_topics

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

        return method in self.successful_methods

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
    # GENERAL ACTIVITY HISTORY
    # =================================================

    def add_history(
        self,
        activity,
        results,
        mistakes=None,
        improvements=None,
        difficulty=None
    ):
        """
        Store a learning activity in history.
        """

        from datetime import datetime

        record = {
            "activity": activity,
            "results": results,
            "mistakes": mistakes or [],
            "improvements": improvements or {},
            "difficulty": difficulty,
            "date": datetime.now().isoformat()
        }

        self.history.append(record)

    def get_history(
        self
    ):

        return self.history

    # =================================================
    # GOAL MEMORY
    # =================================================

    def add_goal(
        self,
        goal
    ):
        """
        Store a learner goal in historical memory.

        Prevents duplicate consecutive goals.
        """

        if self.goal_history:

            last_goal = self.goal_history[-1].get(
                "goal"
            )

            if last_goal == goal:
                return

        self.goal_history.append({
            "goal": goal
        })

    def get_goal_history(
        self
    ):

        return self.goal_history

    def get_last_goal(
        self
    ):

        if not self.goal_history:
            return None

        return self.goal_history[-1].get(
            "goal"
        )

    # =================================================
    # CURRENT GOALS
    # =================================================

    def set_goals(
        self,
        primary=None,
        secondary=None
    ):

        self.goals = {
            "primary": primary,
            "secondary": list(
                secondary or []
            )
        }

    def get_goals(
        self
    ):

        return self.goals

    # =================================================
    # MOTIVATION
    # =================================================

    def update_motivation(
        self,
        category,
        value
    ):

        if category not in self.motivation:
            return

        self.motivation[category] = max(
            0,
            min(
                100,
                value
            )
        )

    def get_motivation(
        self
    ):

        return self.motivation

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

        self.events.append({
            "event": event,
            "data": data
        })

    def get_events(
        self
    ):

        return self.events

    # =================================================
    # MEMORY SUMMARY
    # =================================================

    def get_memory_summary(
        self
    ):

        return {

            # -------------------------------------------------
            # IDENTITY
            # -------------------------------------------------

            "identity": self.identity,

            # -------------------------------------------------
            # CURRENT SKILLS
            # -------------------------------------------------

            "skills": self.skills,

            # -------------------------------------------------
            # CURRENT GOALS
            # -------------------------------------------------

            "goals": self.goals,

            # -------------------------------------------------
            # HISTORICAL GOALS
            # -------------------------------------------------

            "goal_history": self.goal_history,

            # -------------------------------------------------
            # MOTIVATION
            # -------------------------------------------------

            "motivation": self.motivation,

            # -------------------------------------------------
            # ERRORS
            # -------------------------------------------------

            "errors": self.errors,

            # -------------------------------------------------
            # TOPICS
            # -------------------------------------------------

            "completed_topics": self.completed_topics,

            "difficult_topics": self.difficult_topics,

            # -------------------------------------------------
            # METHODS
            # -------------------------------------------------

            "successful_methods": self.successful_methods,

            # -------------------------------------------------
            # PATTERNS
            # -------------------------------------------------

            "patterns": self.patterns,

            # -------------------------------------------------
            # SKILL HISTORY
            # -------------------------------------------------

            "skill_history": self.skill_history,

            # -------------------------------------------------
            # SESSIONS
            # -------------------------------------------------

            "sessions": self.session_history,

            # -------------------------------------------------
            # GENERAL HISTORY
            # -------------------------------------------------

            "history": self.history,

            # -------------------------------------------------
            # PREFERENCES
            # -------------------------------------------------

            "preferences": self.preferences,

            # -------------------------------------------------
            # EVENTS
            # -------------------------------------------------

            "events": self.events,

            # -------------------------------------------------
            # STATISTICS
            # -------------------------------------------------

            "statistics": self.statistics
        }

    # =================================================
    # WEAK AREAS
    # =================================================

    def get_weak_areas(
        self
    ):

        areas = {}

        for error in self.errors:

            skill = error.get("skill")

            if not skill:
                continue

            if skill not in areas:
                areas[skill] = 0

            areas[skill] += error.get(
                "frequency",
                0
            )

        return areas

    # =================================================
    # LOAD MEMORY
    # =================================================

    def load_memory(
        self,
        data
    ):
        """
        Restore memory from a dictionary.

        Supports both the current format and
        older memory files.
        """

        if not isinstance(data, dict):
            return

        # =================================================
        # ERRORS
        # =================================================

        self.errors = data.get(
            "errors",
            []
        )

        # =================================================
        # TOPICS
        # =================================================

        self.completed_topics = data.get(
            "completed_topics",
            []
        )

        self.difficult_topics = data.get(
            "difficult_topics",
            []
        )

        # =================================================
        # METHODS
        # =================================================

        self.successful_methods = data.get(
            "successful_methods",
            []
        )

        # =================================================
        # PATTERNS
        # =================================================

        self.patterns = data.get(
            "patterns",
            []
        )

        # =================================================
        # SKILL HISTORY
        # =================================================

        self.skill_history = data.get(
            "skill_history",
            []
        )

        # =================================================
        # SESSIONS
        # =================================================

        self.session_history = data.get(
            "sessions",
            []
        )

        # =================================================
        # GENERAL HISTORY
        # =================================================

        self.history = data.get(
            "history",
            []
        )

        # =================================================
        # GOAL HISTORY
        # =================================================

        self.goal_history = data.get(
            "goal_history",
            []
        )

        # Backward compatibility:
        # older versions stored goal history
        # under "goals" as a list.

        old_goals = data.get(
            "goals"
        )

        if (
            not self.goal_history
            and isinstance(old_goals, list)
        ):

            self.goal_history = old_goals

        # =================================================
        # PREFERENCES
        # =================================================

        self.preferences = data.get(
            "preferences",
            {}
        )

        # =================================================
        # EVENTS
        # =================================================

        self.events = data.get(
            "events",
            []
        )

        # =================================================
        # IDENTITY
        # =================================================

        saved_identity = data.get(
            "identity"
        )

        if isinstance(saved_identity, dict):

            self.identity.update(
                saved_identity
            )

        # =================================================
        # SKILLS
        # =================================================

        saved_skills = data.get(
            "skills"
        )

        if isinstance(saved_skills, dict):

            self.skills = saved_skills

        # =================================================
        # CURRENT GOALS
        # =================================================

        if isinstance(old_goals, dict):

            self.goals = {
                "primary": old_goals.get(
                    "primary"
                ),
                "secondary": list(
                    old_goals.get(
                        "secondary",
                        []
                    )
                )
            }

        # =================================================
        # MOTIVATION
        # =================================================

        saved_motivation = data.get(
            "motivation"
        )

        if isinstance(saved_motivation, dict):

            self.motivation.update(
                saved_motivation
            )

        # =================================================
        # STATISTICS
        # =================================================

        saved_statistics = data.get(
            "statistics"
        )

        if isinstance(saved_statistics, dict):

            self.statistics.update(
                saved_statistics
            )

    # =================================================
    # SAVE MEMORY
    # =================================================

    def save_memory(
        self,
        path="memory.json"
    ):

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

    def load_from_file(
        self,
        path="memory.json"
    ):

        if not os.path.exists(path):
            return

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        self.load_memory(
            data
        )