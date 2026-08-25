class LevelSystem:
    """
    Converts numerical skill scores
    into CEFR-like levels.
    """


    def __init__(self):

        self.levels = {

            "A1": (0, 20),

            "A2": (21, 40),

            "B1": (41, 60),

            "B2": (61, 75),

            "C1": (76, 90),

            "C2": (91, 100)

        }



    def get_level(self, score):

        """
        Converts score into CEFR level.
        """


        for level, limits in self.levels.items():

            if limits[0] <= score <= limits[1]:

                return level


        return "Unknown"



    def get_description(self, level):

        descriptions = {

            "A1":
            "Can understand and use basic expressions.",


            "A2":
            "Can communicate in simple daily situations.",


            "B1":
            "Can handle everyday conversations and express opinions.",


            "B2":
            "Can communicate comfortably with some complexity.",


            "C1":
            "Can use language effectively in academic and professional contexts.",


            "C2":
            "Near-native proficiency."

        }


        return descriptions.get(
            level,
            "Unknown level"
        )