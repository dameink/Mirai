learning_events = {

    "learning_goal": {
        "keywords": [
            "i want to improve my english",
            "i want to learn english",
            "my goal is",
            "i want to prepare for",
            "i want to get better at"
        ],
        "priority": 1
    },


    "learning_request": {
        "keywords": [
            "can we practice",
            "let's practice",
            "help me learn",
            "teach me",
            "practice english",
            "study with me"
        ],
        "priority": 1
    },


    "exam_preparation": {
        "keywords": [
            "prepare for ielts",
            "prepare for exam",
            "study for test",
            "practice speaking"
        ],
        "priority": 1
    },


    "language_error": {
        "keywords": [
            # возможно пустой,
            # лучше потом через analyzer
        ],
        "priority": 2
    },


    "learning_progress": {
        "keywords": [
            "improved",
            "got better",
            "learned",
            "understand now",
            "finally got it"
        ],
        "priority": 2
    },


    "learning_failure": {
        "keywords": [
            "i don't understand",
            "i can't learn",
            "i keep making mistakes",
            "i struggle with"
        ],
        "priority": 2
    }
}

def detect_learning_event(message):

    text = message.lower()

    detected = None
    highest_priority = 999


    for event, data in learning_events.items():

        for keyword in data["keywords"]:

            if keyword in text:

                if data["priority"] < highest_priority:

                    detected = event
                    highest_priority = data["priority"]


    return detected