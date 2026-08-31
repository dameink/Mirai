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

        Each evidence contains an observed performance value
        and a certainty describing how reliable the observation is.
        """

        updates = []

        for evidence in evidences:
            if evidence is None:
                continue

            result = self.update_skill_from_evidence(
                evidence
            )

            if result is not None:
                updates.append(result)

        self.learner.calculate_overall_level()

        return updates

    # =================================
    # UPDATE ONE EVIDENCE
    # =================================

    def update_skill_from_evidence(self, evidence):
        """
        Update one skill using learning evidence.

        The learner's skill moves toward the observed value.
        Certainty controls how strongly the observation affects
        the learner model.
        """

        category = evidence.category
        skill_name = evidence.skill

        skill = self.learner.get_skill(
            category,
            skill_name
        )

        if skill is None:
            return None

        old_value = skill.get(
            "value",
            0
        )

        observed_value = max(
            0,
            min(
                100,
                evidence.value
            )
        )

        certainty = max(
            0,
            min(
                100,
                evidence.certainty
            )
        )

        # =================================
        # Calculate adjustment
        # =================================

        difference = (
            observed_value - old_value
        )

        adjustment = (
            difference
            * certainty
            / 100
        )

        if abs(adjustment) < 0.01:
            adjustment = 0

        new_value = max(
            0,
            min(
                100,
                old_value + adjustment
            )
        )

        # =================================
        # Update learner
        # =================================

        self.learner.update_skill(
            category,
            skill_name,
            adjustment,
            certainty
        )

        # =================================
        # Return update information
        # =================================

        return {
            "category": category,
            "skill": skill_name,
            "old_value": old_value,
            "observed_value": observed_value,
            "new_value": new_value,
            "adjustment": adjustment,
            "certainty": certainty,
            "source": evidence.source,
            "type": evidence.type,
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

        Used for system events such as learning_progress.

        Normal performance evidence should use
        update_from_evidence().
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

        return {
            "category": category,
            "skill": skill,
            "old_value": old_value,
            "new_value": updated_skill["value"],
            "adjustment": (
                updated_skill["value"]
                - old_value
            ),
            "certainty": updated_skill["certainty"],
            "evidence_count": (
                updated_skill["evidence_count"]
            ),
            "trend": updated_skill["trend"],
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
        Return the current state of one skill.
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
