class LearningStrategy:
    """
    Creates personalized lesson plans
    based on adaptation decisions.
    """



    def __init__(
        self,
        learner
    ):

        self.learner = learner



    # =================================
    # Main lesson creation
    # =================================

    def create_lesson(
        self,
        decision
    ):


        category = (

            decision["focus"]["category"]

        )


        lesson = {


            "focus":
                decision["focus"],


            "difficulty":
                decision["difficulty"],


            "duration":
                self.calculate_duration(),


            "lesson_type":
                self.get_lesson_type(
                    category
                ),


            "steps":
                self.generate_steps(
                    category,
                    decision
                ),


            "correction_style":
                decision["correction"],


            "goal":
                decision["goal"]

        }


        return lesson



    # =================================
    # Duration
    # =================================

    def calculate_duration(self):


        level = self.learner.identity["level"]


        if level == "Unknown":

            return 15


        if level in ["A1", "A2"]:

            return 20


        if level in ["B1", "B2"]:

            return 30


        return 40



    # =================================
    # Lesson type
    # =================================

    def get_lesson_type(
        self,
        category
    ):


        types = {


            "speaking":
                "conversation lesson",


            "grammar":
                "grammar lesson",


            "listening":
                "listening comprehension",


            "reading":
                "reading analysis",


            "writing":
                "writing workshop"

        }


        return types.get(

            category,

            "general practice"

        )



    # =================================
    # Generate lesson steps
    # =================================

    def generate_steps(
        self,
        category,
        decision
    ):


        if category == "speaking":

            return [

                "warm-up conversation",

                "guided speaking task",

                "personalized correction",

                "repeat improved version",

                "reflection"

            ]



        if category == "grammar":

            return [

                "grammar explanation",

                "example analysis",

                "controlled exercises",

                "conversation application",

                "review"

            ]



        if category == "listening":

            return [

                "pre-listening prediction",

                "listening task",

                "comprehension questions",

                "vocabulary extraction",

                "summary"

            ]



        if category == "reading":

            return [

                "text introduction",

                "reading task",

                "main idea discussion",

                "vocabulary analysis",

                "reflection"

            ]



        if category == "writing":

            return [

                "writing prompt",

                "draft creation",

                "feedback",

                "revision",

                "final reflection"

            ]



        return [

            "warm-up",

            decision["activity"],

            "feedback",

            "review"

        ]