class LearningGoal:
    """
    Represents one learning goal.
    """


    def __init__(
        self,
        name,
        description,
        priorities,
        preferred_modes
    ):

        self.name = name

        self.description = description

        self.priorities = priorities

        self.preferred_modes = preferred_modes




class GoalSystem:
    """
    Converts learner goals
    into learning priorities.
    """


    def __init__(
        self,
        learner
    ):

        self.learner = learner

        self.goals = self.create_goals()



    # =================================
    # Available goals
    # =================================

    def create_goals(self):


        return {


            "conversation": LearningGoal(

                "conversation",

                "Improve everyday communication",

                [
                    "speaking",
                    "listening"
                ],

                [
                    "immersion",
                    "casual"
                ]

            ),



            "academic": LearningGoal(

                "academic",

                "Prepare for university and academic communication",

                [
                    "reading",
                    "writing",
                    "academic vocabulary"
                ],

                [
                    "balanced",
                    "intensive"
                ]

            ),



            "ielts": LearningGoal(

                "ielts",

                "Prepare for IELTS examination",

                [
                    "writing",
                    "speaking",
                    "grammar"
                ],

                [
                    "exam",
                    "challenge"
                ]

            ),



            "career": LearningGoal(

                "career",

                "Improve professional communication",

                [
                    "speaking",
                    "vocabulary",
                    "writing"
                ],

                [
                    "immersion",
                    "balanced"
                ]

            ),



            "travel": LearningGoal(

                "travel",

                "Communicate while travelling",

                [
                    "speaking",
                    "listening"
                ],

                [
                    "casual",
                    "immersion"
                ]

            )

        }


    def detect_goal(self, message):

        text = message.lower()

        if "ielts" in text:
            self.set_goal("ielts")
            return "ielts"

        if any(word in text for word in [
            "conversation",
            "speaking",
            "talk"
        ]):
            self.set_goal("conversation")
            return "conversation"

        if any(word in text for word in [
            "academic",
            "university",
            "essay"
        ]):
            self.set_goal("academic")
            return "academic"

        if any(word in text for word in [
            "job",
            "career",
            "professional"
        ]):
            self.set_goal("career")
            return "career"

        if "travel" in text:
            self.set_goal("travel")
            return "travel"


        return None


    # =================================
    # Set goal
    # =================================

    def set_goal(
        self,
        goal_name
    ):


        if goal_name in self.goals:


            self.learner.goals["primary"] = goal_name


            return True



        return False



    # =================================
    # Get current goal
    # =================================

    def get_current_goal(self):


        goal_name = (

            self.learner
            .goals["primary"]

        )


        if goal_name:

            return self.goals.get(
                goal_name
            )


        return None



    # =================================
    # Analyze goal
    # =================================

    def get_goal_strategy(self):


        goal = self.get_current_goal()



        if not goal:


            return {


                "goal":
                    None,


                "priorities":
                    [],


                "preferred_modes":
                    []

            }



        return {


            "goal":
                goal.name,


            "description":
                goal.description,


            "priorities":
                goal.priorities,


            "preferred_modes":
                goal.preferred_modes

        }