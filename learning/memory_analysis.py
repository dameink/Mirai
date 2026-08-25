class MemoryAnalysis:
    """
    Analyzes LearningMemory
    and creates recommendations.
    """

    def __init__(self, memory):

        self.memory = memory
        self.errors = []


    # =================================
    # Errors
    # =================================

    def analyze_errors(self):

        if not hasattr(self.memory, "errors"):

            return {
                "weak_area": None,
                "frequency": 0,
                "priority": "low"
            }


        if not self.memory.errors:

            return {
                "weak_area": None,
                "frequency": 0,
                "priority": "low"
            }


        counter = {}


        for error in self.memory.errors:

            skill = error.get(
                "skill",
                "unknown"
            )


            if skill not in counter:

                counter[skill] = 0


            counter[skill] += (
                error.get(
                    "frequency",
                    1
                )
            )


        weakest = max(
            counter,
            key=counter.get
        )


        return {

            "weak_area":
                weakest,

            "frequency":
                counter[weakest],

            "priority":
                (
                    "high"
                    if counter[weakest] >= 2
                    else "medium"
                )
        }



    # =================================
    # Topics
    # =================================

    def analyze_topics(self):

        topics = getattr(
            self.memory,
            "completed_topics",
            []
        )


        return {

            "completed_topics":
                topics,

            "count":
                len(topics)
        }



    # =================================
    # Methods
    # =================================

    def analyze_methods(self):

        methods = getattr(
            self.memory,
            "successful_methods",
            []
        )


        return {

            "successful_methods":
                methods
        }



    # =================================
    # Full analysis
    # =================================

    def get_analysis(self):

        return {

            "errors":
                self.analyze_errors(),

            "topics":
                self.analyze_topics(),

            "methods":
                self.analyze_methods()
        }