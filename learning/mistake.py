class Mistake:
    """
    Represents learner mistake.
    """


    def __init__(
        self,
        category,
        skill,
        description,
        severity=50,
        frequency=1
    ):

        self.category = category
        self.skill = skill
        self.description = description

        self.severity = severity
        self.frequency = frequency



    def increase_frequency(self):

        self.frequency += 1



    def get_data(self):

        return {

            "category":
                self.category,

            "skill":
                self.skill,

            "description":
                self.description,

            "severity":
                self.severity,

            "frequency":
                self.frequency

        }


class MistakeSystem:
    """
    Stores and analyzes learner mistakes.
    """


    def __init__(
        self,
        learner
    ):

        self.learner = learner

        self.mistakes = []



    # ============================
    # Add mistake
    # ============================

    def add_mistake(
        self,
        mistake
    ):

        for existing in self.mistakes:

            if (
                existing.category == mistake.category
                and
                existing.skill == mistake.skill
                and
                existing.description == mistake.description
            ):

                existing.increase_frequency()

                return existing



        self.mistakes.append(
            mistake
        )

        return mistake



    # ============================
    # Process feedback
    # ============================

    def process_feedback(
        self,
        feedback
    ):


        created = []


        for item in feedback.mistakes:


            mistake = Mistake(

                category="grammar",

                skill="general",

                description=item,

                severity=50

            )


            self.add_mistake(
                mistake
            )


            created.append(
                mistake.get_data()
            )



        return created



    # ============================
    # Find weakest mistakes
    # ============================

    def get_priority_mistakes(
        self
    ):


        sorted_mistakes = sorted(

            self.mistakes,

            key=lambda x:
            (
                x.severity *
                x.frequency
            ),

            reverse=True

        )


        return [

            mistake.get_data()

            for mistake in sorted_mistakes[:5]

        ]



    # ============================
    # Export
    # ============================

    def get_history(
        self
    ):

        return [

            mistake.get_data()

            for mistake in self.mistakes

        ]