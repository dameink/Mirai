from core.emotion import change_emotion


EMOTION_EVENTS = {


    "gratitude": {

        "happiness": 3,
        "trust": 2,
        "comfort": 2

    },


    "compliment": {

        "happiness": 5,
        "trust": 1,
        "comfort": 2,
        "excitement": 2

    },


    "achievement": {

        "happiness": 7,
        "excitement": 5

    },

    "interest": {
        "curiosity": 3,
        "comfort": 1

    },


    "deep_conversation": {

        "comfort": 5,
        "trust": 3,
        "curiosity": 2

    },


    "negative": {

        "happiness": -5,
        "trust": -4,
        "comfort": -5,
        "stress": 5

    },


    "apology": {

        "happiness": 3,
        "trust": 4,
        "comfort": 5,
        "stress": -3

    }

}


def detect_emotion_event(message):

    message = message.lower()


    for event, data in EMOTION_EVENTS.items():

        for keyword in data["keywords"]:

            if keyword in message:

                return event


    return "neutral"


def calculate_intensity(message):

    intensity = 1


    strong_words = [
        "really",
        "very",
        "extremely",
        "truly",
        "so"
    ]


    for word in strong_words:

        if word in message:
            intensity += 1


    return intensity



def process_emotion(message, forced_event=None):

    message = message.lower()

    print(f"Processing emotion for message: {message}")


    intensity = calculate_intensity(message)


    # Если Social Brain уже определил событие
    if forced_event:

        print(
            f"Forced emotion event: {forced_event}"
        )

        apply_emotion_event(
            forced_event,
            intensity
        )

        return forced_event



    # Самостоятельный поиск события

    for event_name, event_data in EMOTION_EVENTS.items():


        for keyword in event_data.get("keywords", []):


            if keyword in message:


                print(
                    f"Detected emotion event: {event_name}"
                )


                apply_emotion_event(
                    event_name,
                    intensity
                )


                return event_name



    print("No emotion event detected")

    return "neutral"


def apply_emotion_event(event_name, intensity=1):

    if event_name not in EMOTION_EVENTS:
        return


    event = EMOTION_EVENTS[event_name]


    print("Applying emotion event:", event_name)


    for emotion, value in event.items():

        change_emotion(
            emotion,
            value * intensity
        )