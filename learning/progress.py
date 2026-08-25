from datetime import datetime


class ProgressTracker:
    """
    Tracks learner improvement,
    learning speed and stability.
    """


    def __init__(self):

        self.history = {}



    # ----------------------------
    # Record progress
    # ----------------------------

    def record(
        self,
        topic,
        value
    ):

        if topic not in self.history:

            self.history[topic] = []


        self.history[topic].append({

            "date": datetime.now(),

            "value": value

        })



    # ----------------------------
    # Get history
    # ----------------------------

    def get_history(
        self,
        topic
    ):

        return self.history.get(
            topic,
            []
        )



    # ----------------------------
    # Learning trend
    # ----------------------------

    def calculate_trend(
        self,
        topic
    ):

        data = self.get_history(topic)


        if len(data) < 2:

            return "not enough data"



        first = data[0]["value"]

        last = data[-1]["value"]


        difference = last - first



        if difference > 5:

            return "improving"


        if difference < -5:

            return "declining"


        return "stable"



    # ----------------------------
    # Learning velocity
    # ----------------------------

    def learning_velocity(
        self,
        topic
    ):


        data = self.get_history(topic)


        if len(data) < 2:

            return 0



        improvement = (

            data[-1]["value"]

            -

            data[0]["value"]

        )


        sessions = len(data) - 1



        return round(

            improvement / sessions,

            2

        )



    # ----------------------------
    # Plateau detection
    # ----------------------------

    def detect_plateau(
        self,
        topic,
        window=3
    ):


        data = self.get_history(topic)


        if len(data) < window:

            return False



        recent = data[-window:]



        values = [

            item["value"]

            for item in recent

        ]



        difference = max(values) - min(values)



        # Almost no movement

        if difference <= 3:

            return True



        return False



    # ----------------------------
    # Stability
    # ----------------------------

    def calculate_stability(
        self,
        topic
    ):


        data = self.get_history(topic)


        if len(data) < 2:

            return 0



        values = [

            item["value"]

            for item in data

        ]


        average = sum(values) / len(values)



        deviations = [

            abs(value - average)

            for value in values

        ]


        stability = 100 - (

            sum(deviations)

            /

            len(values)

        )



        return round(

            max(0, stability),

            2

        )



    # ----------------------------
    # Mastery confidence
    # ----------------------------

    def mastery_confidence(
        self,
        topic
    ):


        data = self.get_history(topic)


        if len(data) == 0:

            return 0



        stability = self.calculate_stability(
            topic
        )


        sessions = min(
            len(data) * 10,
            50
        )



        return round(

            (

                stability * 0.6

                +

                sessions * 0.4

            ),

            2

        )