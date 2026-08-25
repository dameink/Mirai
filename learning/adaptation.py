from learning.memory_analysis import MemoryAnalysis


class Adaptation:
    """
    Creates personalized learning strategy.

    Uses:
    - learner state
    - learning memory
    - emotions
    - progress
    - knowledge state

    Goal:
    Choose the best next learning action.
    """

    def __init__(
        self,
        learner,
        memory=None,
        emotion=None,
        progress=None,
        knowledge_state=None,
        state=None
    ):

        self.learner = learner
        self.memory = memory

        if self.memory:
            self.memory_analysis = MemoryAnalysis(
                self.memory
            )
        else:
            self.memory_analysis = None

        self.emotion = emotion
        self.progress = progress
        self.knowledge_state = knowledge_state
        self.state = state


    # =================================
    # MAIN STRATEGY
    # =================================

    def create_strategy(self):

        memory_data = self.analyze_memory()

        priority = self.find_priority_skill(
            memory_data
        )


        if priority is None:
            return {
                "focus": None,
                "activity": "free conversation",
                "difficulty": "assessment",
                "correction": "encouraging correction",
                "goal": "collect learning data"
            }


        return {
            "focus": priority,

            "activity":
                self.choose_activity(
                    priority
                ),

            "difficulty":
                self.calculate_difficulty(
                    priority
                ),

            "correction":
                self.choose_correction_style(),

            "goal":
                self.define_session_goal(
                    priority
                ),

            "reason":
                self.get_reason(
                    priority
                )
        }



    # =================================
    # MEMORY ANALYSIS
    # =================================

    def analyze_memory(self):

        if not self.memory_analysis:
            return None

        return (
            self.memory_analysis
            .get_analysis()
        )



    # =================================
    # FIND PRIORITY SKILL
    # =================================

    def find_priority_skill(
        self,
        memory_data=None
    ):

        memory_priority = None


        # -------------------------
        # Memory detected weakness
        # -------------------------

        if memory_data:

            weak_area = (
                memory_data
                .get("errors", {})
                .get("weak_area")
            )


            if weak_area:

                memory_priority = {
                    "category": weak_area,
                    "skill": weak_area,
                    "score": 100,
                    "reason":
                        "Detected from learning memory"
                }



        best = None
        highest = -1


        for category, skills in (
            self.learner.skills.items()
        ):

            for skill, data in skills.items():

                score = 0

                reason = (
                    "Calculated from learner performance."
                )


                # =========================
                # Memory influence
                # =========================

                if memory_data:

                    weak_area = (
                        memory_data
                        ["errors"]
                        ["weak_area"]
                    )


                    if weak_area == category:

                        score += 40

                        reason = (
                            f"{category} selected because "
                            "memory detected repeated mistakes."
                        )



                # =========================
                # Unknown knowledge
                # =========================

                if data["evidence_count"] == 0:

                    score -= 20



                # =========================
                # Weak skill
                # =========================

                score += (
                    100 -
                    data["value"]
                ) * 0.35



                # =========================
                # Low confidence
                # =========================

                score += (
                    100 -
                    data["certainty"]
                ) * 0.2



                # =========================
                # Memory score
                # =========================

                score += (
                    self.memory_score(
                        category
                    )
                )



                # =========================
                # IELTS priority
                # =========================

                if (
                    self.learner.goals["primary"]
                    ==
                    "ielts"
                ):

                    if category in [
                        "writing",
                        "speaking",
                        "grammar"
                    ]:

                        score += 20



                # =========================
                # Progress
                # =========================

                if self.progress:

                    if (
                        self.progress
                        .detect_plateau(skill)
                    ):

                        score += 15


                    if (
                        self.progress
                        .learning_velocity(skill)
                        > 5
                    ):

                        score -= 10



                if score > highest:

                    highest = score

                    best = {

                        "reason": reason,

                        "category":
                            category,

                        "skill":
                            skill,

                        "score":
                            round(
                                score,
                                2
                            )
                    }



        # Memory has strongest priority

        if memory_priority:
            return memory_priority


        return best



    # =================================
    # MEMORY SCORE
    # =================================

    def memory_score(
        self,
        category
    ):

        if not self.memory:

            return 0


        score = 0


        for error in getattr(
            self.memory,
            "errors",
            []
        ):

            if (
                error["skill"]
                ==
                category
            ):

                frequency = (
                    error.get(
                        "frequency",
                        1
                    )
                )

                severity = (
                    error.get(
                        "severity",
                        50
                    )
                )


                score += (
                    frequency * 5
                    +
                    severity * 0.2
                )


        return score



    # =================================
    # ACTIVITY
    # =================================

    def choose_activity(
        self,
        priority
    ):

        category = priority["category"]
        skill = priority["skill"]


        data = self.learner.get_skill(
            category,
            skill
        )


        value = data["value"]



        if category == "grammar":

            if (
                self.learner
                .learning_preferences
                ["prefers_explanations"]
            ):

                return (
                    "grammar explanation "
                    "with IELTS examples"
                )


            return (
                "grammar correction practice"
            )



        if category == "speaking":

            if value < 50:

                return (
                    "guided conversation practice"
                )

            return (
                "IELTS speaking challenge"
            )



        if category == "writing":

            return (
                "IELTS Writing Task 2 practice"
            )



        if category == "listening":

            return (
                "listening comprehension task"
            )



        if category == "reading":

            return (
                "reading analysis task"
            )



        return "free conversation"



    # =================================
    # DIFFICULTY
    # =================================

    def calculate_difficulty(
        self,
        priority
    ):

        data = self.learner.get_skill(
            priority["category"],
            priority["skill"]
        )


        effective = (
            data["value"]
            *
            data["certainty"]
            /
            100
        )


        if effective < 30:

            return "beginner"


        if effective < 70:

            return "intermediate"


        return "advanced"



    # =================================
    # CORRECTION
    # =================================

    def choose_correction_style(
        self
    ):

        intensity = (
            self.learner
            .learning_preferences
            ["correction_intensity"]
        )


        if intensity < 40:

            return "soft correction"


        if intensity < 70:

            return "balanced correction"


        return "direct correction"



    # =================================
    # GOAL
    # =================================

    def define_session_goal(
        self,
        priority
    ):

        category = priority["category"]
        skill = priority["skill"]


        if category == "grammar":

            return (
                f"improve {skill} "
                "accuracy"
            )


        if category == "speaking":

            return (
                "improve speaking "
                "fluency and confidence"
            )


        if category == "writing":

            return (
                "improve IELTS writing "
                "performance"
            )


        return (
            f"improve {category} "
            "through practice"
        )



    # =================================
    # EXPLANATION
    # =================================

    def get_reason(
        self,
        priority
    ):

        return (
            f"Selected {priority['category']} "
            f"{priority['skill']} because "
            "it has highest learning priority."
        )