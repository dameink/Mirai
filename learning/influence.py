class LearningInfluence:

    def __init__(self, learning):
        self.learning = learning


    def analyze(
        self,
        message,
        context,
        event
    ):

        influence = {
            "should_teach": False,
            "focus": None,
            "activity": None,
            "strategy": None,
            "intensity": 0,
            "reason": None
        }


        if event == "learning_goal":

            influence["should_teach"] = True
            influence["focus"] = "goal discovery"
            influence["activity"] = "conversation assessment"

            influence["strategy"] = {
                "action": "discover learner",
                "collect": [
                    "current level",
                    "learning goal",
                    "preferred activity"
                ]
            }

            influence["intensity"] = 30

            influence["reason"] = (
                "User expressed learning goal"
            )


        elif event == "learning_request":

            influence["should_teach"] = True
            influence["focus"] = "practice"
            influence["activity"] = "guided speaking practice"

            influence["strategy"] = {
                "action": "start practice",
                "skill": "speaking",
                "mode": "conversation"
            }

            influence["intensity"] = 60


        elif event == "exam_preparation":

            influence["should_teach"] = True
            influence["focus"] = "exam preparation"
            influence["activity"] = "IELTS speaking practice"

            influence["strategy"] = {
                "action": "exam training",
                "exam": "IELTS",
                "skill": "speaking"
            }

            influence["intensity"] = 70


        elif event == "learning_failure":

            influence["should_teach"] = True
            influence["focus"] = "weakness recovery"
            influence["activity"] = "explanation"

            influence["strategy"] = {
                "action": "explain",
                "mode": "support"
            }

            influence["intensity"] = 40


        elif event == "learning_progress":

            influence["should_teach"] = True
            influence["focus"] = "progress reinforcement"
            influence["activity"] = "challenge"

            influence["strategy"] = {
                "action": "increase difficulty",
                "mode": "adaptive"
            }

            influence["intensity"] = 50


        return influence