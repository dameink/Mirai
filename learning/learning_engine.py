from learning.controller import LearningController


class LearningEngine:
    """
    Main interface for Mirai Learning System.

    Core should communicate only with this class.

    Flow:

    User
      ↓
    Learning Engine
      ↓
    Learning Controller
      ↓
    Learning Systems
      ↓
    Result
    """



    def __init__(
        self,
        learner
    ):

        self.learner = learner


        # Existing learning architecture

        self.controller = LearningController(
            learner
        )



        # Current session

        self.current_session = None



    # =================================
    # Analyze learner
    # =================================


    def analyze(self):

        return (

            self.controller
            .analyze()

        )



    # =================================
    # Start learning session
    # =================================


    def start_session(self):


        self.current_session = (

            self.controller
            .start_session()

        )


        return self.current_session.get_summary()



    # =================================
    # Submit user result
    # =================================


    def submit_result(
        self,
        result
    ):

        """
        Example:

        {
            "fluency":75,
            "grammar":60
        }

        """



        updates = (

            self.controller
            .process_result(
                result
            )

        )



        if self.current_session:


            self.current_session.complete(

                result=result,

                improvements=updates

            )



        return {


            "updates":
                updates,


            "next_strategy":
                self.controller
                .get_next_strategy()

        }



    # =================================
    # Complete activity
    # =================================


    def complete_activity(
        self,
        result
    ):


        response = (
            self.controller
            .complete_activity(result)
        )


        if self.current_session:


            self.current_session.complete(

                result=result,

                improvements=response["updates"]

            )


        return response



    # =================================
    # Get learner profile
    # =================================


    def get_profile(self):


        return (

            self.controller
            .get_learning_profile()

        )



    # =================================
    # Main learning function
    # =================================


    def learn(
        self,
        result=None
    ):

        """
        Main function Mirai Core will call.

        Example:

        learning.learn()

        -> creates lesson


        learning.learn(result)

        -> updates learner

        """



        if result is None:


            return self.start_session()



        else:


            return self.complete_activity(
                result
            )