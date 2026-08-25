class DifficultyLevel:


    def __init__(
        self,
        name,
        score,
        description
    ):

        self.name=name
        self.score=score
        self.description=description




class DifficultySystem:


    def __init__(
        self,
        learner,
        state=None,
        goal_system=None,
        mode_system=None
    ):

        self.learner=learner
        self.state=state
        self.goal_system=goal_system
        self.mode_system=mode_system

        self.levels=self.create_levels()



    def create_levels(self):

        return {


            "easy":DifficultyLevel(
                "easy",
                30,
                "Building confidence"
            ),


            "normal":DifficultyLevel(
                "normal",
                50,
                "Balanced learning difficulty"
            ),


            "challenging":DifficultyLevel(
                "challenging",
                70,
                "Requires active thinking"
            ),


            "advanced":DifficultyLevel(
                "advanced",
                90,
                "Pushes learner beyond comfort zone"
            )

        }



    def calculate_score(self):


        score=40



        motivation=self.learner.motivation


        if motivation["effort"]>80:

            score+=10


        elif motivation["effort"]<40:

            score-=15



        confidence=self.learner.skills["speaking"]["confidence"]


        if confidence["certainty"]>40:


            if confidence["value"]>70:

                score+=10


            elif confidence["value"]<40:

                score-=10




        if self.mode_system:


            mode=self.mode_system.determine_mode().name


            if mode=="challenge":

                score+=15


            elif mode=="support":

                score-=5


            elif mode=="exam":

                score+=5




        return max(
            0,
            min(
                100,
                score
            )
        )




    def get_difficulty(self):


        score=self.calculate_score()


        if score<40:

            level=self.levels["easy"]


        elif score<60:

            level=self.levels["normal"]


        elif score<80:

            level=self.levels["challenging"]


        else:

            level=self.levels["advanced"]



        return {

            "difficulty":level.name,
            "score":score,
            "description":level.description

        }