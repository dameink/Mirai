from .evidence import Evidence
from .diagnosis import Diagnosis


class Assessment:
    """
    Analyzes user interactions
    and creates learning evidence.

    Assessment does NOT directly modify
    the learner model.

    Flow:

        Message
           ↓
        Error detection
           ↓
        Evidence
           ↓
        Diagnosis
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

    # =================================
    # Analyze message
    # =================================

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

            results.append({
                "evidence": evidence.get_data(),
                "diagnosis": diagnosis
            })

        return results

    # =================================
    # Error detection
    # =================================

    def detect_errors(
        self,
        message
    ):
        errors = []

        text = message.lower()

        # ---------------------------------
        # Grammar — Tenses
        # ---------------------------------

        if "goed" in text:

            errors.append({
                "category": "grammar",
                "topic": "Past Simple",
                "skill": "tenses",
                "type": "mistake",
                "severity": 3,
                "confidence": 90,
            })

        # ---------------------------------
        # Grammar — Word order
        # ---------------------------------

        if "i am agree" in text:

            errors.append({
                "category": "grammar",
                "topic": "Sentence Structure",
                "skill": "word_order",
                "type": "mistake",
                "severity": 2,
                "confidence": 80,
            })

        return errors

    # =================================
    # Create evidence
    # =================================

    def create_evidence(
        self,
        error
    ):
        """
        Convert detected mistake
        into an observed performance.

        The current skill is used as
        the baseline and the mistake
        produces a lower observation.

        SkillUpdateSystem is responsible
        for changing the actual learner skill.
        """

        skill = self.learner.get_skill(
            error["category"],
            error["skill"]
        )

        current_value = (
            skill["value"]
            if skill
            else 0
        )

        # Severity:
        # 1 = minor
        # 5 = major
        penalty = error["severity"] * 10

        observed_value = max(
            0,
            current_value - penalty
        )

        return Evidence(
            skill=error["skill"],
            category=error["category"],
            value=observed_value,
            topic=error["topic"],
            evidence_type=error["type"],
            source="conversation",
            certainty=error["confidence"],
            context="conversation",
            difficulty=None,
        )