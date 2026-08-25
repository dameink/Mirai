class LearningMode:
    """
    Represents one learning mode.
    """

    def __init__(
        self,
        name,
        description,
        intensity,
        focus,
        strategy_hint
    ):

        self.name = name
        self.description = description
        self.intensity = intensity
        self.focus = focus
        self.strategy_hint = strategy_hint



class ModeSystem:
    """
    Selects optimal learning mode
    based on learner condition.
    """

    def __init__(
        self,
        learner,
        goal_system=None
    ):

        self.learner = learner
        self.goal_system = goal_system

        self.modes = self.create_modes()



    # =================================
    # Available modes
    # =================================

    def create_modes(self):

        return {


            "discovery": LearningMode(
                "discovery",
                "Exploring learner abilities",
                30,
                "assessment",
                "collect information and build learner profile"
            ),


            "support": LearningMode(
                "support",
                "Building confidence and reducing frustration",
                40,
                "confidence",
                "use easier tasks and positive reinforcement"
            ),


            "balanced": LearningMode(
                "balanced",
                "Normal personalized learning",
                60,
                "progress",
                "maintain steady improvement"
            ),


            "challenge": LearningMode(
                "challenge",
                "Pushing learner beyond comfort zone",
                90,
                "growth",
                "increase difficulty and introduce complex tasks"
            ),


            "exam": LearningMode(
                "exam",
                "Structured exam preparation",
                90,
                "performance",
                "timed tasks and detailed feedback"
            ),


            "confidence": LearningMode(
                "confidence",
                "Building speaking confidence",
                40,
                "confidence",
                "create small wins"
            ),


            "vocabulary": LearningMode(
                "vocabulary",
                "Expanding vocabulary range",
                60,
                "vocabulary",
                "learn words through context"
            ),


            "immersion": LearningMode(
                "immersion",
                "Learning through natural interaction",
                70,
                "communication",
                "focus on conversation"
            ),


            "review": LearningMode(
                "review",
                "Strengthening existing knowledge",
                50,
                "memory",
                "practice weak areas"
            )

        }



    # =================================
    # Evidence calculation
    # =================================

    def get_total_evidence(self):

        total = 0


        for category, skills in self.learner.skills.items():

            for skill, data in skills.items():

                total += data["evidence_count"]


        return total



    # =================================
    # Readiness
    # =================================

    def get_readiness(self):

        values = []


        for category, skills in self.learner.skills.items():

            for skill, data in skills.items():

                if data["certainty"] > 0:

                    values.append(
                        data["value"]
                    )


        if not values:

            return 30


        return sum(values) / len(values)



    # =================================
    # Confidence
    # =================================

    def get_confidence_score(self):

        confidence = (

            self.learner
            .skills["speaking"]
            ["confidence"]

        )


        if confidence["certainty"] < 40:

            return None


        return confidence["value"]



    # =================================
    # Decision system
    # =================================

    def determine_mode(self):


        scores = {


            "discovery": 0,

            "support": 0,

            "balanced": 0,

            "challenge": 0,

            "exam": 0,

            "confidence": 0,

            "vocabulary": 0


        }



        motivation = self.learner.motivation


        effort = motivation["effort"]

        engagement = motivation["engagement"]


        level = self.learner.identity["level"]



        evidence = self.get_total_evidence()

        readiness = self.get_readiness()

        confidence = self.get_confidence_score()



        # =================================
        # New learner
        # =================================

        if (

            level == "Unknown"

            and

            evidence < 3

        ):

            scores["discovery"] += 100



        # =================================
        # Motivation
        # =================================

        if (

            effort < 40

            or

            engagement < 40

        ):

            scores["support"] += 50



        elif (

            effort > 80

            and

            engagement > 80

        ):

            scores["balanced"] += 20



        # =================================
        # Goal influence
        # =================================

        if self.goal_system:


            goal = self.goal_system.get_goal_strategy()



            if goal["goal"] == "ielts":


                if level == "B1":

                    scores["balanced"] += 40



                elif level in ["B2", "C1", "C2"]:

                    scores["exam"] += 40




            for mode in goal["preferred_modes"]:


                if mode == "challenge":


                    if (

                        readiness > 60

                        and

                        evidence > 3

                    ):

                        scores["challenge"] += 40



                elif mode in scores:

                    scores[mode] += 20



        # =================================
        # Confidence
        # =================================

        if confidence is not None:


            if confidence < 30:

                scores["confidence"] += 40



            elif confidence > 75:

                scores["challenge"] += 20



        # =================================
        # Skill readiness
        # =================================

        if evidence > 3:


            if readiness < 40:

                scores["support"] += 20



            elif readiness > 70:

                scores["challenge"] += 20



        # =================================
        # Advanced learners
        # =================================

        if (

            level in ["B2", "C1", "C2"]

            and

            readiness > 60

            and

            effort > 70

        ):

            scores["challenge"] += 30



        # =================================
        # Select
        # =================================

        best_mode = max(

            scores,

            key=scores.get

        )


        return self.modes[best_mode]



    # =================================
    # Current state
    # =================================

    def get_current_state(self):


        mode = self.determine_mode()


        return {


            "mode":
                mode.name,


            "description":
                mode.description,


            "intensity":
                mode.intensity,


            "focus":
                mode.focus,


            "strategy_hint":
                mode.strategy_hint

        }