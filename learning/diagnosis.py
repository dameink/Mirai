class Diagnosis:
    """
    Analyzes evidence and determines
    the reason behind learning problems.
    """


    def __init__(self, knowledge_state):

        self.knowledge_state = knowledge_state



    # ---------------------------------
    # Main diagnosis function
    # ---------------------------------

    def analyze(
        self,
        evidence
    ):

        diagnosis = {

            "topic": None,

            "problem_type": None,

            "severity": None,

            "recommendation": None

        }


        topic = self.identify_topic(
            evidence
        )


        diagnosis["topic"] = topic



        diagnosis["problem_type"] = (
            self.identify_problem(
                topic
            )
        )


        diagnosis["severity"] = (
            self.calculate_severity(
                topic
            )
        )


        diagnosis["recommendation"] = (
            self.get_recommendation(
                diagnosis["problem_type"]
            )
        )


        return diagnosis



    # ---------------------------------
    # Find language topic
    # ---------------------------------

    def identify_topic(
        self,
        evidence
    ):

        """
        Later this will use AI/NLP.

        For now we use evidence data.
        """

        return evidence.get(
            "topic",
            "Unknown"
        )



    # ---------------------------------
    # Understand problem
    # ---------------------------------

    def identify_problem(
        self,
        topic
    ):


        if topic == "Unknown":

            return "unknown"



        knowledge = (
            self.knowledge_state
            .get_topic_state(topic)
        )


        if knowledge is None:

            return "unknown"



        mastery = knowledge["mastery"]



        if mastery < 30:

            return "knowledge_gap"


        elif mastery < 70:

            return "needs_practice"


        else:

            return "performance_issue"



    # ---------------------------------
    # Severity
    # ---------------------------------

    def calculate_severity(
        self,
        topic
    ):


        knowledge = (
            self.knowledge_state
            .get_topic_state(topic)
        )


        mastery = knowledge["mastery"]



        if mastery < 30:

            return "high"


        elif mastery < 70:

            return "medium"


        return "low"



    # ---------------------------------
    # Recommendation
    # ---------------------------------

    def get_recommendation(
        self,
        problem_type
    ):


        recommendations = {


            "knowledge_gap":
            "explain concept and practice basics",


            "needs_practice":
            "practice through conversation",


            "performance_issue":
            "increase difficulty",


            "unknown":
            "collect more information"

        }


        return recommendations.get(
            problem_type
        )