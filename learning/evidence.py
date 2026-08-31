from datetime import datetime


class Evidence:
    """
    Represents one learning observation.

    Flow:
        Activity / Conversation
                ↓
             Evidence
                ↓
            Diagnosis
                ↓
        SkillUpdateSystem
                ↓
          Learner profile
    """

    def __init__(
        self,
        skill,
        category,
        value,
        topic,
        evidence_type,
        source="activity",
        certainty=50,
        context="conversation",
        difficulty=None,
    ):
        self.skill = skill
        self.category = category
        self.topic = topic

        # Observed performance.
        # Always keep inside 0-100.
        self.value = max(
            0,
            min(100, value)
        )

        self.type = evidence_type
        self.source = source

        # Reliability of this observation.
        self.certainty = max(
            0,
            min(100, certainty)
        )

        self.context = context
        self.difficulty = difficulty

        self.created_at = datetime.now()

    # =================================
    # Evidence weight
    # =================================

    def calculate_weight(self):
        weight = self.certainty

        if self.difficulty == "advanced":
            weight += 20

        elif self.difficulty == "challenging":
            weight += 10

        return min(
            100,
            weight
        )

    # =================================
    # Convert to update
    # =================================

    def get_update(self):
        return {
            "category": self.category,
            "skill": self.skill,
            "topic": self.topic,
            "value": self.value,
            "certainty": self.certainty,
            "weight": self.calculate_weight(),
            "source": self.source,
            "type": self.type,
            "context": self.context,
            "difficulty": self.difficulty,
            "created_at": self.created_at,
        }

    # =================================
    # Export
    # =================================

    def get_data(self):
        return {
            "skill": self.skill,
            "category": self.category,
            "topic": self.topic,
            "value": self.value,
            "type": self.type,
            "source": self.source,
            "certainty": self.certainty,
            "context": self.context,
            "difficulty": self.difficulty,
            "created_at": self.created_at,
        }