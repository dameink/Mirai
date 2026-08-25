class SkillUpdateSystem:
    """
    Updates learner skills based on evidence.

    Flow:

    Feedback
        ↓
    Evidence
        ↓
    Skill Update
        ↓
    Learner Profile
        ↓
    Level recalculation
    """



    def __init__(
        self,
        learner
    ):

        self.learner = learner



    # =================================
    # Update one skill
    # =================================

    def update_skill(
        self,
        evidence
    ):


        category = evidence.category

        skill = evidence.skill



        skill_data = (
            self.learner
            .skills
            [category]
            [skill]
        )



        old_value = skill_data["value"]

        old_certainty = skill_data["certainty"]

        old_count = skill_data["evidence_count"]



        # =============================
        # Calculate new value
        # =============================


        if old_count == 0:

            new_value = evidence.value


        else:

            new_value = (

                old_value * old_count

                +

                evidence.value

            ) / (

                old_count + 1

            )



        new_value = round(
            new_value,
            2
        )



        # =============================
        # Update certainty
        # =============================


        new_certainty = min(

            100,

            old_certainty

            +

            evidence.certainty * 0.25

        )


        new_certainty = round(
            new_certainty,
            2
        )



        # =============================
        # Trend
        # =============================


        if new_value > old_value:

            trend = 1


        elif new_value < old_value:

            trend = -1


        else:

            trend = 0



        # =============================
        # Save changes
        # =============================


        skill_data["value"] = new_value

        skill_data["certainty"] = new_certainty

        skill_data["evidence_count"] = old_count + 1

        skill_data["trend"] = trend



        # =============================
        # Recalculate learner level
        # =============================


        self.learner.calculate_overall_level()



        return skill_data



    # =================================
    # Update multiple evidences
    # =================================

    def update_from_evidence(
        self,
        evidences
    ):


        updates = []



        for evidence in evidences:


            updated_skill = self.update_skill(
                evidence
            )


            updates.append(
                updated_skill
            )



        # final level update

        self.learner.calculate_overall_level()



        return updates



    # =================================
    # Get skill status
    # =================================

    def get_skill_status(
        self,
        category,
        skill
    ):


        return (

            self.learner
            .skills
            [category]
            [skill]

        )