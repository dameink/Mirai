from learning.learner import Learner
from learning.learning_events import detect_learning_event
from core.learning_bridge import LearningBridge


def run_test(message):

    print("\n==============================")
    print("MESSAGE:")
    print(message)


    learner = Learner(
        native_language="Russian",
        learning_language="English"
    )


    bridge = LearningBridge(
        learner
    )


    event = detect_learning_event(message)

    print("\nLEARNING EVENT:")
    print(event)


    influence = bridge.get_learning_influence(
        event,
        message
    )

    print("\nLEARNING INFLUENCE:")
    print(influence)


    if event:
        learner.process_learning_event(
            event,
            message
        )


    print("\nUPDATED PROFILE:")
    print(
        learner.get_profile()
    )



tests = [

    "Hi Mirai, I want to improve my English",

    "I want to prepare for IELTS speaking. My goal is band 8",

    "Can we practice English today?",

    "I improved my speaking skills",

    "I don't understand this grammar topic"

]


for message in tests:
    run_test(message)