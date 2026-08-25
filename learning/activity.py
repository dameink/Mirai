class LearningActivity:
    """
    Represents one learning activity.
    """


    def __init__(
        self,
        name,
        skill,
        subskill,
        activity_type,
        difficulty,
        duration,
        description
    ):

        self.name = name
        self.skill = skill
        self.subskill = subskill
        self.type = activity_type
        self.difficulty = difficulty
        self.duration = duration
        self.description = description



    def get_data(self):

        return {

            "name": self.name,

            "skill": self.skill,

            "subskill": self.subskill,

            "type": self.type,

            "difficulty": self.difficulty,

            "duration": self.duration,

            "description": self.description

        }





class ActivitySystem:
    """
    Adaptive activity generation system.
    """


    def __init__(
        self,
        learner,
        state=None,
        goal_system=None,
        mode_system=None,
        difficulty_system=None
    ):


        self.learner = learner

        self.state = state

        self.goal_system = goal_system

        self.mode_system = mode_system

        self.difficulty_system = difficulty_system


        self.activities = self.create_activities()



    # =================================
    # Activity database
    # =================================


    def create_activities(self):

        return [

            LearningActivity(
                "General Speaking Practice",
                "speaking",
                "fluency",
                "conversation",
                "normal",
                15,
                "Practice everyday speaking through guided conversation"
            ),

            LearningActivity(
                "IELTS Speaking Part 2",
                "speaking",
                "fluency",
                "speaking",
                "normal",
                15,
                "Describe a topic and speak for two minutes"
            ),

            LearningActivity(
                "Grammar Tenses Practice",
                "grammar",
                "tenses",
                "grammar",
                "normal",
                20,
                "Practice tense accuracy through exercises"
            ),

            LearningActivity(
                "Article Accuracy Training",
                "grammar",
                "articles",
                "grammar",
                "normal",
                15,
                "Practice article usage in sentences"
            ),

            LearningActivity(
                "Academic Vocabulary Training",
                "vocabulary",
                "range",
                "vocabulary",
                "normal",
                20,
                "Learn and use academic vocabulary"
            ),

            LearningActivity(
                "IELTS Writing Task 2",
                "writing",
                "structure",
                "writing",
                "challenging",
                40,
                "Write an argumentative essay"
            ),

            LearningActivity(
                "Listening Practice",
                "listening",
                "general",
                "listening",
                "normal",
                20,
                "Listen and answer comprehension questions"
            )

        ]



    # =================================
    # Weakest skill
    # =================================


    def get_weakest_skill(self):


        if not self.state:

            return None



        weakest = self.state.get_weakest_skill()


        if not weakest:

            return None



        return weakest



    # =================================
    # Difficulty
    # =================================


    def get_current_difficulty(self):


        if self.difficulty_system:


            return (

                self.difficulty_system
                .get_difficulty()
                ["difficulty"]

            )


        return "normal"



    # =================================
    # Select activity
    # =================================


    def select_activity(self):

        goal = None

        if self.goal_system:
            goal = self.goal_system.get_goal_strategy()

        if hasattr(self.learner, "last_strategy"):

            strategy = self.learner.last_strategy

            if strategy:

                focus = strategy.get("focus", {})

                category = focus.get("category")
                skill = focus.get("skill")

                for activity in self.activities:

                    if (
                        activity.skill == category
                        and activity.subskill == skill
                    ):
                        return activity
                
        weakest = self.get_weakest_skill()

        if weakest:
            category = weakest.get("category")
            skill = weakest.get("skill")
        else:
            category = None
            skill = None


        # IELTS priority
        if goal and goal["goal"] == "ielts":

            for activity in self.activities:

                if activity.name.startswith("IELTS"):

                    if category in [
                        "speaking",
                        "writing"
                    ]:
                        return activity


        candidates = []

        for activity in self.activities:

            if activity.subskill == skill:
                candidates.append(activity)

            elif activity.skill == category:
                candidates.append(activity)


        if not candidates:

            for activity in self.activities:
                if activity.name == "General Speaking Practice":
                    return activity

            candidates = self.activities


        return candidates[0]

    # =================================
    # Public API
    # =================================


    def generate_activity(self):


        activity = (

            self.select_activity()

        )


        return activity.get_data()