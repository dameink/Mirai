from evidence import Evidence
from diagnosis import Diagnosis


class Assessment:
    """
    Analyzes user interactions
    and creates learning evidence.
    """


    def __init__(
        self,
        learner,
        knowledge_state
    ):

        self.learner = learner

        self.knowledge_state = knowledge_state

        self.diagnosis = Diagnosis(
            knowledge_state
        )



    # ----------------------------
    # Analyze message
    # ----------------------------

    def analyze_message(
        self,
        message
    ):

        errors = self.detect_errors(
            message
        )


        results = []


        for error in errors:


            evidence = self.create_evidence(
                error
            )


            diagnosis = self.diagnosis.analyze(
                evidence.get_data()
            )


            self.apply_evidence(
                evidence
            )


            results.append({

                "evidence":
                    evidence.get_data(),

                "diagnosis":
                    diagnosis

            })


        return results



    # ----------------------------
    # Error detection
    # ----------------------------

    def detect_errors(
        self,
        message
    ):


        errors = []


        text = message.lower()



        if "goed" in text:


            errors.append({

                "category":
                    "grammar",


                "topic":
                    "Past Simple",


                "skill":
                    "tenses",


                "type":
                    "mistake",


                "severity":
                    3,


                "confidence":
                    90


            })



        if "i am agree" in text:


            errors.append({

                "category":
                    "grammar",


                "topic":
                    "Sentence Structure",


                "skill":
                    "word_order",


                "type":
                    "mistake",


                "severity":
                    2,


                "confidence":
                    80


            })


        return errors



    # ----------------------------
    # Create evidence
    # ----------------------------

    def create_evidence(
        self,
        error
    ):


        impact = -error["severity"]



        return Evidence(

            topic=error["topic"],

            category=error["category"],

            evidence_type=error["type"],

            impact=impact,

            certainty=error["confidence"],

            context="conversation",

            difficulty=None

        )



    # ----------------------------
    # Apply evidence
    # ----------------------------

    def apply_evidence(
        self,
        evidence
    ):


        topic = evidence.topic



        # Update knowledge state

        self.knowledge_state.update_topic(

            topic,

            evidence.impact,

            evidence.certainty

        )



        # Update learner model

        skill = self.learner.get_skill(

            evidence.category,

            "tenses"

        )


        if skill:


            new_value = max(

                0,

                skill["value"]
                + evidence.impact

            )


            self.learner.update_skill(

                evidence.category,

                "tenses",

                new_value,

                evidence.certainty

            )



            self.learner.add_history(

                topic,

                evidence.impact,

                evidence.type

            )