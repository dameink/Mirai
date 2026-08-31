from .level import LevelSystem
from learning.learning_memory import LearningMemory
from learning.storage import MemoryStorage


class Learner:
    """
    Represents the user's learning profile.

    Stores:
    - identity
    - goals
    - skills
    - learning preferences
    - motivation
    - learning history
    - persistent learning memory
    """

    def __init__(
        self,
        native_language="",
        learning_language="English"
    ):
        # =================================================
        # IDENTITY
        # =================================================

        self.identity = {
            "native_language": native_language,
            "learning_language": learning_language,
            "level": "Unknown"
        }

        # =================================================
        # GOALS
        # =================================================

        self.goals = {
            "primary": None,
            "secondary": []
        }

        # =================================================
        # LEARNING PREFERENCES
        # =================================================

        self.learning_preferences = {
            "preferred_activity": None,
            "correction_preference": None,
            "prefers_conversation": True,
            "prefers_explanations": True,
            "likes_corrections": True,
            "correction_intensity": 50
        }

        # =================================================
        # LEVEL SYSTEM
        # =================================================

        self.level_system = LevelSystem()

        # =================================================
        # SKILLS
        # =================================================

        self.skills = self.create_default_skills()

        # =================================================
        # HISTORY
        # =================================================

        self.history = []

        # =================================================
        # MOTIVATION
        # =================================================

        self.motivation = {
            "consistency": 50,
            "effort": 50,
            "engagement": 50
        }

        # =================================================
        # PERSISTENT MEMORY
        # =================================================

        self.learning_memory = LearningMemory()
        self.memory_storage = MemoryStorage()

        saved_memory = self.memory_storage.load()

        if saved_memory:
            self.learning_memory.load_memory(
                saved_memory
            )

            self.restore_from_memory()

    # =================================================
    # CREATE SKILL
    # =================================================

    def create_skill(self):
        return {
            "value": 0,
            "certainty": 0,
            "evidence_count": 0,
            "trend": 0
        }

    # =================================================
    # CREATE DEFAULT SKILLS
    # =================================================

    def create_default_skills(self):
        """
        Create the complete default skill structure.

        Persistent memory must never be able to remove
        categories or skills from this structure.
        """

        return {
            "speaking": {
                "fluency": self.create_skill(),
                "pronunciation": self.create_skill(),
                "confidence": self.create_skill(),
                "accuracy": self.create_skill()
            },

            "listening": {
                "general": self.create_skill(),
                "native_speed": self.create_skill()
            },

            "reading": {
                "comprehension": self.create_skill()
            },

            "writing": {
                "structure": self.create_skill(),
                "task_response": self.create_skill()
            },

            "grammar": {
                "tenses": self.create_skill(),
                "articles": self.create_skill(),
                "word_order": self.create_skill()
            },

            "vocabulary": {
                "range": self.create_skill(),
                "collocations": self.create_skill()
            }
        }

    # =================================================
    # RESTORE LEARNER FROM MEMORY
    # =================================================

    def restore_from_memory(self):
        """
        Restore learner state from persistent memory.

        Persistent memory contains historical/current data,
        but it must NEVER replace the default skill structure.

        Missing categories and skills remain initialized.
        Existing saved values are merged into them.
        """

        # =================================================
        # IDENTITY
        # =================================================

        saved_identity = self.learning_memory.identity

        if saved_identity:
            self.identity.update(
                saved_identity
            )

        # =================================================
        # GOAL
        # =================================================

        last_goal = (
            self.learning_memory
            .get_last_goal()
        )

        if last_goal:
            self.goals["primary"] = last_goal

        # =================================================
        # CURRENT MEMORY SKILLS
        # =================================================

        saved_skills = (
            self.learning_memory.skills
        )

        if saved_skills:

            for category, skills in saved_skills.items():

                # Ignore unknown categories
                if category not in self.skills:
                    continue

                if not isinstance(skills, dict):
                    continue

                for skill, data in skills.items():

                    # Ignore unknown skills
                    if skill not in self.skills[category]:
                        continue

                    if not isinstance(data, dict):
                        continue

                    # Merge saved data into default skill
                    self.skills[category][skill].update(
                        data
                    )

        # =================================================
        # RECONSTRUCT SKILLS FROM HISTORY
        # =================================================

        history = (
            self.learning_memory.skill_history
        )

        if history:

            for item in history:

                if not isinstance(item, dict):
                    continue

                skill_path = item.get("skill")

                if not skill_path:
                    continue

                parts = skill_path.split(".")

                if len(parts) != 2:
                    continue

                category = parts[0]
                skill = parts[1]

                if category not in self.skills:
                    continue

                if skill not in self.skills[category]:
                    continue

                current = self.skills[category][skill]

                # Only use history when it contains a value
                if "value" in item:
                    current["value"] = item["value"]

                current["evidence_count"] = max(
                    current.get("evidence_count", 0),
                    1
                )

        # =================================================
        # PREFERENCES
        # =================================================

        saved_preferences = (
            self.learning_memory.preferences
        )

        if saved_preferences:

            for key, value in saved_preferences.items():

                if key in self.learning_preferences:

                    self.learning_preferences[key] = value

    # =================================================
    # GOALS
    # =================================================

    def set_goal(
        self,
        primary,
        secondary=None
    ):
        self.goals["primary"] = primary

        self.learning_memory.add_goal(
            primary
        )

        self.memory_storage.save(
            self.learning_memory
        )

        if secondary:
            self.goals["secondary"] = secondary

    # =================================================
    # INITIALIZE PROFILE
    # =================================================

    def initialize_profile(
        self,
        level="B1",
        motivation=None
    ):
        self.identity["level"] = level

        if motivation:

            for key, value in motivation.items():

                if key in self.motivation:

                    self.motivation[key] = value

    # =================================================
    # SKILLS
    # =================================================

    def update_skill(
        self,
        category,
        skill,
        value_change,
        certainty_change
    ):
        # Safety check
        if category not in self.skills:
            return

        if skill not in self.skills[category]:
            return

        current = self.skills[category][skill]

        old_value = current["value"]

        new_value = max(
            0,
            min(
                100,
                old_value + value_change
            )
        )

        current["value"] = new_value

        current["evidence_count"] += 1

        current["certainty"] = min(
            100,
            current["certainty"]
            +
            (
                certainty_change
                /
                current["evidence_count"]
            )
        )

        current["trend"] = (
            new_value - old_value
        )

        # =================================================
        # SAVE PROGRESS HISTORY
        # =================================================

        self.learning_memory.add_skill_progress(
            f"{category}.{skill}",
            new_value
        )

        # =================================================
        # SAVE CURRENT SKILL STATE
        # =================================================

        self.learning_memory.skills = self.skills

        self.memory_storage.save(
            self.learning_memory
        )

    # =================================================
    # GET SKILL
    # =================================================

# =================================================
# GET SKILL
# =================================================

    def get_skill(
        self,
        category,
        skill
    ):
        """
        Safely return a skill.

        Unknown categories/skills are created dynamically,
        but category names are never treated as skills.
        """

        # Prevent category from becoming a skill
        if skill == category:
            default_skills = {
                "speaking": "fluency",
                "listening": "general",
                "reading": "comprehension",
                "writing": "structure",
                "grammar": "tenses",
                "vocabulary": "range"
            }

            skill = default_skills.get(category)

            if skill is None:
                return None

        # Unknown category
        if category not in self.skills:
            self.skills[category] = {}

        # Unknown skill
        if skill not in self.skills[category]:
            self.skills[category][skill] = self.create_skill()

        return self.skills[category][skill]

    # =================================================
    # GET SKILL LEVEL
    # =================================================

    def get_skill_level(
        self,
        category,
        skill
    ):
        score = (
            self.get_skill(
                category,
                skill
            )["value"]
        )

        return self.level_system.get_level(
            score
        )

    # =================================================
    # CATEGORY AVERAGE
    # =================================================

    def get_category_average(
        self,
        category
    ):
        if category not in self.skills:
            return None

        skills = self.skills[category]

        values = []

        for skill in skills.values():

            if not isinstance(skill, dict):
                continue

            if skill.get("evidence_count", 0) > 0:

                values.append(
                    skill.get("value", 0)
                )

        if not values:
            return None

        return sum(values) / len(values)

    # =================================================
    # OVERALL LEVEL
    # =================================================

    def calculate_overall_level(self):

        evidence_total = 0

        for category in self.skills.values():

            for skill in category.values():

                if isinstance(skill, dict):

                    evidence_total += (
                        skill.get(
                            "evidence_count",
                            0
                        )
                    )

        if evidence_total < 3:

            self.identity["level"] = "Unknown"

            return "Unknown"

        weights = {
            "speaking": 0.35,
            "listening": 0.25,
            "reading": 0.20,
            "writing": 0.20
        }

        total = 0
        weight_used = 0

        for category, weight in weights.items():

            average = (
                self.get_category_average(
                    category
                )
            )

            if average is not None:

                total += (
                    average * weight
                )

                weight_used += weight

        if weight_used == 0:

            self.identity["level"] = "Unknown"

            return "Unknown"

        total = (
            total
            /
            weight_used
        )

        level = (
            self.level_system.get_level(
                total
            )
        )

        self.identity["level"] = level

        return level

    # =================================================
    # LEARNING EVENT
    # =================================================

    def process_learning_event(
        self,
        event,
        message
    ):
        message_lower = message.lower()

        if event == "learning_goal":

            if "ielts" in message_lower:

                self.set_goal(
                    "ielts"
                )

            elif "english" in message_lower:

                self.set_goal(
                    "conversation"
                )

            self.history.append({
                "event": event,
                "message": message
            })

        elif event == "learning_request":

            self.update_preference(
                "preferred_activity",
                "conversation"
            )

            self.learning_preferences[
                "prefers_conversation"
            ] = True

        elif event == "learning_progress":

            if "speaking" in message_lower:

                self.update_skill(
                    "speaking",
                    "fluency",
                    5,
                    10
                )

        elif event == "learning_failure":

            self.motivation[
                "engagement"
            ] = max(
                0,
                self.motivation["engagement"] - 5
            )

    # =================================================
    # HISTORY
    # =================================================

    def add_history(
        self,
        activity,
        results,
        mistakes=None,
        improvements=None,
        difficulty=None
    ):
        from datetime import datetime

        record = {
            "activity": activity,
            "results": results,
            "mistakes": mistakes or [],
            "improvements": improvements or {},
            "difficulty": difficulty,
            "date": datetime.now().isoformat()
        }

        self.history.append(
            record
        )

    # =================================================
    # PREFERENCES
    # =================================================

    def update_preference(
        self,
        key,
        value
    ):
        if key in self.learning_preferences:

            self.learning_preferences[key] = value

            self.learning_memory.update_preference(
                key,
                value
            )

            self.memory_storage.save(
                self.learning_memory
            )

    # =================================================
    # LEARNING EVENT
    # =================================================

    def add_learning_event(
        self,
        event,
        message
    ):
        self.history.append({
            "event": event,
            "message": message
        })

        self.learning_memory.add_event(
            event,
            message
        )

        self.memory_storage.save(
            self.learning_memory
        )

    # =================================================
    # MOTIVATION
    # =================================================

    def update_motivation(
        self,
        category,
        value
    ):
        if category in self.motivation:

            self.motivation[category] = max(
                0,
                min(
                    100,
                    value
                )
            )

    # =================================================
    # PROFILE
    # =================================================

    def get_profile(self):

        return {
            "identity":
                self.identity,

            "goals":
                self.goals,

            "skills":
                self.skills,

            "learning_preferences":
                self.learning_preferences,

            "motivation":
                self.motivation,

            "history":
                self.history,

            "memory":
                self.learning_memory.get_memory_summary()
        }


# =====================================================
# TEST
# =====================================================

if __name__ == "__main__":

    user = Learner(
        native_language="Russian",
        learning_language="English"
    )

    user.update_skill(
        "speaking",
        "fluency",
        55,
        70
    )

    user.update_skill(
        "listening",
        "general",
        75,
        80
    )

    print(
        user.calculate_overall_level()
    )

    print(
        user.get_profile()
    )