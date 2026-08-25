class KnowledgeState:

    def __init__(
        self,
        knowledge_map,
        progress_tracker=None
    ):

        self.knowledge_map = knowledge_map

        self.progress_tracker = progress_tracker

        self.state = {}

        self.initialize_state()



    # ---------------------------------
    # Create initial learner knowledge
    # ---------------------------------

    def initialize_state(self):

        for topic in self.knowledge_map.nodes:

            self.state[topic] = {

                "mastery": 0,

                "confidence": 0,

                "attempts": 0,

                "successes": 0,

                "mistakes": 0,

                "last_practiced": None

            }



    # ---------------------------------
    # Update knowledge
    # ---------------------------------

    def update_topic(
        self,
        topic,
        impact,
        confidence
    ):

        if topic not in self.state:
            return


        knowledge = self.state[topic]


        old_mastery = knowledge["mastery"]


        knowledge["mastery"] = max(
            0,
            min(
                100,
                old_mastery + impact
            )
        )


        if self.progress_tracker:

            self.progress_tracker.record(
                topic,
                knowledge["mastery"]
            )


        knowledge["confidence"] = min(
            100,
            knowledge["confidence"] + confidence
        )


        knowledge["attempts"] += 1

    # ---------------------------------
    # Get topic knowledge
    # ---------------------------------

    def get_topic_state(
        self,
        topic
    ):

        return self.state.get(topic)



    # ---------------------------------
    # Find weak topics
    # ---------------------------------

    def get_weak_topics(
        self,
        limit=5
    ):


        sorted_topics = sorted(

            self.state.items(),

            key=lambda x: x[1]["mastery"]

        )


        return sorted_topics[:limit]



    # ---------------------------------
    # Summary
    # ---------------------------------

    def get_summary(self):

        return self.state