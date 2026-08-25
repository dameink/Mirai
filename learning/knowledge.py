class KnowledgeNode:
    """
    Represents one language concept.
    """


    def __init__(
        self,
        name,
        category,
        level,
        prerequisites=None
    ):

        self.name = name

        self.category = category

        self.level = level

        self.prerequisites = prerequisites or []



    def get_info(self):

        return {

            "name": self.name,

            "category": self.category,

            "level": self.level,

            "prerequisites": self.prerequisites

        }



class KnowledgeMap:
    """
    Represents the whole language structure.
    """


    def __init__(self):

        self.nodes = {}

        self.create_default_map()



    # ---------------------------------
    # Add knowledge
    # ---------------------------------

    def add_node(
        self,
        node
    ):

        self.nodes[node.name] = node



    # ---------------------------------
    # Default English map
    # ---------------------------------

    def create_default_map(self):


        # Grammar

        self.add_node(
            KnowledgeNode(
                "Present Simple",
                "Grammar",
                "A1"
            )
        )


        self.add_node(
            KnowledgeNode(
                "Past Simple",
                "Grammar",
                "A2",
                [
                    "Present Simple"
                ]
            )
        )


        self.add_node(
            KnowledgeNode(
                "Present Perfect",
                "Grammar",
                "B1",
                [
                    "Past Simple"
                ]
            )
        )


        self.add_node(
            KnowledgeNode(
                "Conditionals",
                "Grammar",
                "B2",
                [
                    "Present Perfect"
                ]
            )
        )



        # Vocabulary


        self.add_node(
            KnowledgeNode(
                "Daily Vocabulary",
                "Vocabulary",
                "A1"
            )
        )


        self.add_node(
            KnowledgeNode(
                "Academic Vocabulary",
                "Vocabulary",
                "B2",
                [
                    "Daily Vocabulary"
                ]
            )
        )



        # Speaking


        self.add_node(
            KnowledgeNode(
                "Basic Conversation",
                "Speaking",
                "A1"
            )
        )


        self.add_node(
            KnowledgeNode(
                "Expressing Opinions",
                "Speaking",
                "B1",
                [
                    "Basic Conversation"
                ]
            )
        )


        self.add_node(
            KnowledgeNode(
                "Debate Skills",
                "Speaking",
                "C1",
                [
                    "Expressing Opinions"
                ]
            )
        )



    # ---------------------------------
    # Search
    # ---------------------------------

    def get_topic(
        self,
        name
    ):

        return self.nodes.get(name)



    def get_topics_by_category(
        self,
        category
    ):

        return [

            node

            for node in self.nodes.values()

            if node.category == category

        ]