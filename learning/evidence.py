from datetime import datetime



class Evidence:
    """
    Represents one learning observation.

    Evidence is created after:
    Activity
        ->
    Feedback
        ->
    Evidence
        ->
    Skill Update
    """



    def __init__(
        self,
        skill,
        category,
        value,
        evidence_type,
        source="activity",
        certainty=50,
        context="conversation",
        difficulty=None
    ):


        # Skill name
        # Example:
        # fluency, grammar, vocabulary

        self.skill = skill


        # Category:
        # speaking, writing, listening...

        self.category = category



        # Observed performance value

        self.value = value



        # Type of evidence

        # feedback
        # assessment
        # activity

        self.type = evidence_type



        # Where evidence came from

        self.source = source



        # How reliable this observation is

        self.certainty = certainty



        # Situation

        self.context = context



        # Task difficulty

        self.difficulty = difficulty



        # Creation time

        self.created_at = datetime.now()



    # =================================
    # Evidence weight
    # =================================

    def calculate_weight(self):


        weight = self.certainty



        # Harder tasks give stronger evidence

        if self.difficulty == "advanced":

            weight += 20


        elif self.difficulty == "challenging":

            weight += 10



        # Limit

        weight = min(
            100,
            weight
        )


        return weight



    # =================================
    # Convert to skill update
    # =================================

    def get_update(self):


        return {


            "category":
                self.category,


            "skill":
                self.skill,


            "value":
                self.value,


            "certainty":
                self.certainty,


            "weight":
                self.calculate_weight(),


            "source":
                self.source,


            "type":
                self.type,


            "created_at":
                self.created_at

        }



    # =================================
    # Export
    # =================================

    def get_data(self):


        return {


            "skill":
                self.skill,


            "category":
                self.category,


            "value":
                self.value,


            "type":
                self.type,


            "source":
                self.source,


            "certainty":
                self.certainty,


            "context":
                self.context,


            "difficulty":
                self.difficulty,


            "created_at":
                self.created_at

        }