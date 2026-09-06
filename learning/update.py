class SkillUpdateSystem:
    """
    Updates learner skills based on learning evidence.

    Flow:

        Evidence
            ↓
        SkillUpdateSystem
            ↓
        Learner
            ↓
        Learning Memory
    """

    def __init__(self, learner):
        self.learner = learner

    # =================================
    # UPDATE FROM EVIDENCE
    # =================================

    def update_from_evidence(self, evidences):
        """
        Apply a list of Evidence objects.
        """

        updates = []

        if not evidences:
            self.learner.calculate_overall_level()
            return updates

        for evidence in evidences:
            if evidence is None:
                continue

            result = self.update_skill_from_evidence(evidence)

            if result is not None:
                updates.append(result)

        self.learner.calculate_overall_level()

        return updates

    # =================================
    # UPDATE ONE EVIDENCE
    # =================================

    def update_skill_from_evidence(self, evidence):
        """
        Update one learner skill from one Evidence object.
        """

        if evidence is None:
            return None

        category = getattr(evidence, "category", None)
        skill_name = getattr(evidence, "skill", None)

        if not category or not skill_name:
            return None

        # ---------------------------------
        # Find the learner skill
        # ---------------------------------

        skill = self.learner.get_skill(
            category,
            skill_name
        )

        # If the skill does not exist, do not
        # silently pretend that an update happened.
        if skill is None:
            return None

        old_value = float(
            skill.get("value", 0)
        )

        observed_value = max(
            0,
            min(
                100,
                float(getattr(evidence, "value", 0))
            )
        )

        certainty = max(
            0,
            min(
                100,
                float(getattr(evidence, "certainty", 0))
            )
        )

        # ---------------------------------
        # Calculate adjustment
        # ---------------------------------

        difference = observed_value - old_value

        adjustment = (
            difference
            * certainty
            / 100
        )

        if abs(adjustment) < 0.01:
            adjustment = 0

        # ---------------------------------
        # Update learner
        # ---------------------------------

        updated_skill = self.learner.update_skill(
            category,
            skill_name,
            adjustment,
            certainty
        )

        # Get the actual state after update.
        current_skill = self.learner.get_skill(
            category,
            skill_name
        )

        if current_skill is None:
            return None

        new_value = current_skill.get(
            "value",
            old_value
        )

        return {
            "category": category,
            "skill": skill_name,
            "old_value": old_value,
            "observed_value": observed_value,
            "new_value": new_value,
            "adjustment": adjustment,
            "certainty": current_skill.get(
                "certainty",
                0
            ),
            "evidence_count": current_skill.get(
                "evidence_count",
                0
            ),
            "trend": current_skill.get(
                "trend",
                0
            ),
            "source": getattr(
                evidence,
                "source",
                "conversation"
            ),
            "type": getattr(
                evidence,
                "type",
                "conversation"
            ),
        }

    # =================================
    # DIRECT SKILL UPDATE
    # =================================

    def update_skill(
        self,
        category,
        skill,
        value_change,
        certainty_change
    ):
        """
        Direct low-level skill update.
        """

        skill_data = self.learner.get_skill(
            category,
            skill
        )

        if skill_data is None:
            return None

        old_value = skill_data.get(
            "value",
            0
        )

        self.learner.update_skill(
            category,
            skill,
            value_change,
            certainty_change
        )

        updated_skill = self.learner.get_skill(
            category,
            skill
        )

        if updated_skill is None:
            return None

        return {
            "category": category,
            "skill": skill,
            "old_value": old_value,
            "new_value": updated_skill.get(
                "value",
                old_value
            ),
            "adjustment": (
                updated_skill.get(
                    "value",
                    old_value
                ) - old_value
            ),
            "certainty": updated_skill.get(
                "certainty",
                0
            ),
            "evidence_count": updated_skill.get(
                "evidence_count",
                0
            ),
            "trend": updated_skill.get(
                "trend",
                0
            ),
        }

    # =================================
    # GET SKILL STATUS
    # =================================

    def get_skill_status(
        self,
        category,
        skill
    ):
        """
        Return current state of one skill.
        """

        skill_data = self.learner.get_skill(
            category,
            skill
        )

        if skill_data is None:
            return None

        return {
            "category": category,
            "skill": skill,
            "value": skill_data.get(
                "value",
                0
            ),
            "certainty": skill_data.get(
                "certainty",
                0
            ),
            "evidence_count": skill_data.get(
                "evidence_count",
                0
            ),
            "trend": skill_data.get(
                "trend",
                0
            ),
        }