class LearningState:
    """
    Represents current condition
    of the learner.
    """


    def __init__(
        self,
        learner
    ):

        self.learner = learner



    # ==========================
    # Level
    # ==========================

    def get_level(self):

        return (
            self.learner
            .identity["level"]
        )



    # ==========================
    # Motivation
    # ==========================

    def get_motivation(self):

        return (

            self.learner
            .motivation

        )



    # ==========================
    # Average confidence
    # ==========================

    def get_confidence(self):


        fluency = (
            self.learner
            .skills["speaking"]
            ["fluency"]
            ["value"]
        )


        pronunciation = (
            self.learner
            .skills["speaking"]
            ["pronunciation"]
            ["value"]
        )


        accuracy = (
            self.learner
            .skills["speaking"]
            ["accuracy"]
            ["value"]
        )


        confidence = (

            fluency * 0.5 +

            pronunciation * 0.3 +

            accuracy * 0.2

        )


        return round(confidence)


    # ==========================
    # Find weakest skill
    # ==========================

    def get_weakest_skill(self):


        weakest = None

        lowest = 101


        for category, skills in self.learner.skills.items():

            for skill, data in skills.items():


                # ignore untested skills

                if data["evidence_count"] == 0:

                    continue


                if data["value"] < lowest:

                    lowest = data["value"]


                    weakest = {

                        "category": category,

                        "skill": skill,

                        "value": data["value"]

                    }



        # if nothing tested yet

        if weakest is None:

            return {

                "category": None,

                "skill": None,

                "value": 0

            }


        return weakest



    # ==========================
    # Learning summary
    # ==========================

    def get_state(self):


        return {


            "level":
                self.get_level(),


            "motivation":
                self.get_motivation(),


            "confidence":
                self.get_confidence(),


            "weakest_skill":
                self.get_weakest_skill()

        }