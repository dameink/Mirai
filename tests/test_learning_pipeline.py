from core.learning_bridge import LearningBridge
from learning.learner import Learner


learner = Learner(
    native_language="Russian",
    learning_language="English"
)


bridge = LearningBridge(
    learner
)


tests = [
    "Hi Mirai, I want to improve my English",
    "I want to prepare for IELTS speaking. My goal is band 8",
    "Can we practice English today?",
    "I don't understand this grammar topic",
    "I improved my speaking skills"
]


for message in tests:

    print("\n==============================")
    print("MESSAGE:")
    print(message)


    result = bridge.process_message(
        message
    )


    print("\nEVENT:")
    print(
        result["event"]
    )


    print("\nINFLUENCE:")
    print(
        result["influence"]
    )


    print("\nPROFILE:")
    print(
        result["profile"]
    )