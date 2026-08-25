class Feedback:
    """
    Stores feedback result.
    """


    def __init__(
        self,
        strengths,
        weaknesses,
        mistakes,
        recommendation,
        scores
    ):

        self.strengths = strengths
        self.weaknesses = weaknesses
        self.mistakes = mistakes
        self.recommendation = recommendation
        self.scores = scores



    def get_feedback(self):

        return {

            "strengths":
                self.strengths,

            "weaknesses":
                self.weaknesses,

            "mistakes":
                self.mistakes,

            "recommendation":
                self.recommendation,

            "scores":
                self.scores

        }





class FeedbackSystem:
    """
    Analyzes learner performance
    and generates feedback.
    """



    def __init__(
        self,
        learner
    ):

        self.learner = learner



    # =================================
    # Analyze activity result
    # =================================

    def analyze(
        self,
        activity,
        performance
    ):


        strengths = []

        weaknesses = []

        mistakes = []



        scores = performance.get(
            "scores",
            {}
        )



        # -----------------------------
        # Speaking
        # -----------------------------

        if activity["skill"] == "speaking":


            fluency = scores.get(
                "fluency",
                0
            )


            grammar = scores.get(
                "grammar",
                0
            )


            vocabulary = scores.get(
                "vocabulary",
                0
            )


            pronunciation = scores.get(
                "pronunciation",
                0
            )



            if fluency >= 70:

                strengths.append(
                    "good fluency"
                )

            else:

                weaknesses.append(
                    "fluency needs improvement"
                )



            if grammar >= 70:

                strengths.append(
                    "good grammar accuracy"
                )

            else:

                weaknesses.append(
                    "grammar mistakes"
                )

                mistakes.append(
                    "grammar errors during speaking"
                )



            if vocabulary >= 70:

                strengths.append(
                    "wide vocabulary"
                )

            else:

                weaknesses.append(
                    "limited vocabulary range"
                )



            if pronunciation >= 70:

                strengths.append(
                    "clear pronunciation"
                )

            else:

                weaknesses.append(
                    "pronunciation practice needed"
                )



        # -----------------------------
        # Writing
        # -----------------------------

        elif activity["skill"] == "writing":


            grammar = scores.get(
                "grammar",
                0
            )


            structure = scores.get(
                "structure",
                0
            )



            if structure >= 70:

                strengths.append(
                    "good essay structure"
                )

            else:

                weaknesses.append(
                    "weak organization"
                )



            if grammar >= 70:

                strengths.append(
                    "accurate grammar"
                )

            else:

                weaknesses.append(
                    "grammar accuracy issues"
                )

                mistakes.append(
                    "grammar mistakes in writing"
                )



        # -----------------------------
        # Recommendation
        # -----------------------------


        recommendation = self.generate_recommendation(
            weaknesses
        )



        return Feedback(

            strengths,

            weaknesses,

            mistakes,

            recommendation,

            scores

        )



    # =================================
    # Recommendation
    # =================================

    def generate_recommendation(
        self,
        weaknesses
    ):


        if not weaknesses:

            return (
                "Continue practicing "
                "to maintain progress."
            )



        if "grammar mistakes" in weaknesses:

            return (
                "Review grammar rules "
                "and practice accuracy."
            )


        if "fluency needs improvement" in weaknesses:

            return (
                "Practice speaking "
                "with timed responses."
            )


        if "limited vocabulary range" in weaknesses:

            return (
                "Expand vocabulary "
                "through contextual learning."
            )


        return (
            "Practice weak areas "
            "with additional activities."
        )