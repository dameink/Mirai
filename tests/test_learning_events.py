from learning.learning_events import detect_learning_event
from core.learning_bridge import LearningBridge
from learning.learner import Learner
from core.learning_context import LearningContext


# ==========================
# CREATE LEARNING SYSTEM
# ==========================

learner = Learner(
    native_language="",
    learning_language="English"
)


bridge = LearningBridge(
    learner
)


context = LearningContext(
    bridge
)


# ==========================
# TEST CASES
# ==========================

tests = [

    "Hi Mirai, I want to improve my English",

    "I want to prepare for IELTS speaking. My goal is band 8",

    "Can we practice English today?",

    "Please correct my grammar mistakes",

    "I don't understand this grammar topic",

    "I improved my speaking skills",

    "I prefer learning through conversations",

]


# ==========================
# RUN TESTS
# ==========================

for message in tests:

    print("\n==============================")
    print("MESSAGE:")
    print(message)


    event = detect_learning_event(
        message
    )


    print("\nLEARNING EVENT:")
    print(event)


    print("\nLEARNING INFLUENCE:")

    influence = bridge.get_learning_influence(
        message,
        context
    )

    print(influence)


    print("\nLEARNING PROFILE:")

    profile = context.get_context()

    print(
        profile
    )