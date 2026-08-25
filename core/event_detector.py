# core/event_detector.py


EVENTS = {


    "gratitude": {
        "keywords": [
            "thanks",
            "thank you",
            "thank",
            "appreciate",
            "i appreciate",
            "grateful",
            "i am grateful",
            "i'm grateful",
            "i owe you",
            "that helped me",
            "you helped me"
        ],
        "priority": 3
    },


    "compliment": {
        "keywords": [
            "amazing",
            "awesome",
            "great",
            "beautiful",
            "smart",
            "cute",
            "nice",
            "good",
            "cool",
            "impressive",
            "wonderful",
            "excellent",
            "brilliant",
            "you are helpful",
            "you are funny",
            "you are kind"
        ],
        "priority": 1
    },


    "achievement": {
        "keywords": [
            "passed",
            "finished",
            "completed",
            "created",
            "built",
            "won",
            "achieved",
            "succeeded",
            "finally did it",
            "made it",
            "accomplished",
            "solved",
            "managed to",
            "i got accepted",
            "i got a good score",
            "i improved",
            "i learned"
        ],
        "priority": 3
    },


    "apology": {
        "keywords": [
            "sorry",
            "my bad",
            "forgive me",
            "apologize",
            "i apologize",
            "i didn't mean to",
            "that was my mistake",
            "my fault"
        ],
        "priority": 4
    },


    "interest": {
        "keywords": [
            "i like",
            "i love",
            "i enjoy",
            "my favorite",
            "i am interested in",
            "i'm interested in",
            "i am passionate about",
            "i am into",
            "i really like",
            "i'm fascinated by",
            "i enjoy learning about"
        ],
        "priority": 2
    },


    "failure": {
        "keywords": [
            "i failed",
            "i fail",
            "i didn't pass",
            "i did not pass",
            "i got a bad grade",
            "i got a low score",
            "i couldn't pass",
            "i couldn't do it",
            "i messed up",
            "i lost",
            "i made a mistake",
            "i performed badly",
            "i struggled",
            "i wasn't able to",
            "it didn't work",
            "i disappointed myself"
        ],
        "priority": 3
    },


    "negative": {
        "keywords": [
            "stupid",
            "useless",
            "hate",
            "terrible",
            "annoying",
            "awful",
            "bad",
            "worst",
            "disgusting",
            "frustrating",
            "angry",
            "mad",
            "upset"
        ],
        "priority": 5
    },


    "deep_conversation": {
        "keywords": [
            "my dream",
            "my future",
            "my feelings",
            "my life",
            "i feel",
            "i worry about",
            "i am afraid",
            "i am scared",
            "my purpose",
            "what matters to me",
            "my values",
            "who i am",
            "what should i do with my life"
        ],
        "priority": 1
    },

    "goal": {
        "keywords": [
            "i want to",
            "i plan to",
            "my goal is",
            "i hope to",
            "i want become",
            "i want to become",
            "i am trying to",
            "i aim to",
            "i would like to"
        ],
        "priority": 3
    },


    "curiosity": {
        "keywords": [
            "why",
            "how",
            "what do you think",
            "i wonder",
            "i am curious",
            "tell me more",
            "explain",
            "can you explain"
        ],
        "priority": 1
    },


    "confusion": {
        "keywords": [
            "i don't understand",
            "i dont understand",
            "i am confused",
            "i'm confused",
            "i don't get it",
            "what does this mean",
            "how does this work"
        ],
        "priority": 3
    },


    "frustration": {
        "keywords": [
            "this is hard",
            "this is difficult",
            "i am struggling",
            "i can't do this",
            "i am frustrated",
            "so difficult",
            "too hard"
        ],
        "priority": 4
    },


    "decision": {
        "keywords": [
            "i decided",
            "i chose",
            "i changed my mind",
            "i will",
            "i'm going to",
            "i have decided"
        ],
        "priority": 2
    },


    "opinion": {
        "keywords": [
            "i think",
            "i believe",
            "in my opinion",
            "personally",
            "i feel like"
        ],
        "priority": 1
    },


    "memory_reference": {
        "keywords": [
            "remember",
            "do you remember",
            "as i said",
            "before",
            "last time"
        ],
        "priority": 4
    }

}



def detect_event(message):

    message = message.lower()


    detected = []


    for event_name, data in EVENTS.items():

        for keyword in data["keywords"]:

            if keyword in message:

                detected.append(
                    (
                        event_name,
                        data["priority"]
                    )
                )

                break



    if not detected:

        return {

            "event": "neutral",

            "confidence": 0

        }



    # выбираем событие с самым высоким priority

    detected.sort(
        key=lambda x: x[1],
        reverse=True
    )


    return {

        "event": detected[0][0],

        "confidence": 1

    }

def calculate_event_intensity(message):

    message = message.lower()

    intensity = 1


    strong_words = [

        "really",
        "very",
        "truly",
        "extremely",
        "so much",
        "incredible"

    ]


    for word in strong_words:

        if word in message:

            intensity += 1


    return intensity