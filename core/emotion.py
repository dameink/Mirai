import json
import os


EMOTION_FILE = "emotion.json"


DEFAULT_EMOTION = {

    "state": {

        "happiness": 70,
        "energy": 80,
        "trust": 50,
        "curiosity": 80,
        "comfort": 60,
        "excitement": 50,
        "stress": 20

    },


    "emotional_style": {

        "expressiveness": 75,
        "sensitivity": 60,
        "recovery_speed": 80

    }
}

EMOTION_BASELINE = {

    "happiness": 70,
    "energy": 80,
    "trust": 50,
    "curiosity": 80,
    "comfort": 60,
    "excitement": 50,
    "stress": 20

}


def load_emotion():

    if not os.path.exists(EMOTION_FILE):

        save_emotion(DEFAULT_EMOTION)
        return DEFAULT_EMOTION


    try:

        with open(EMOTION_FILE, "r") as file:

            return json.load(file)


    except json.JSONDecodeError:

        save_emotion(DEFAULT_EMOTION)
        return DEFAULT_EMOTION



def save_emotion(emotion):

    with open(EMOTION_FILE, "w") as file:

        json.dump(emotion, file, indent=4)



def change_emotion(emotion_name, amount):

    emotion = load_emotion()


    if emotion_name in emotion["state"]:

        emotion["state"][emotion_name] += amount


        emotion["state"][emotion_name] = max(
            0,
            min(
                100,
                emotion["state"][emotion_name]
            )
        )


    save_emotion(emotion)



def get_emotion():

    return load_emotion()

def reset_emotion():

    save_emotion(DEFAULT_EMOTION)

def emotional_reaction():

    emotion = load_emotion()

    state = emotion["state"]


    if state["stress"] > 70:
        return "Mirai feels stressed."


    if state["energy"] < 30:
        return "Mirai feels tired."


    if state["happiness"] > 80:
        return "Mirai feels very happy 😊"


    if state["trust"] > 75:
        return "Mirai feels comfortable with you."


    if state["curiosity"] > 85:
        return "Mirai is curious."


    return "Mirai feels normal."

def decay_emotions():

    emotion = load_emotion()

    state = emotion["state"]


    decay_rates = {

        "happiness": 1,
        "energy": 1,
        "curiosity": 1,
        "comfort": 0.5,
        "excitement": 1,
        "stress": -1,
        "trust": 0.2

    }




    for emotion_name, rate in decay_rates.items():

        if emotion_name in state:

            if state[emotion_name] > EMOTION_BASELINE[emotion_name]:

                state[emotion_name] -= rate


            elif state[emotion_name] < EMOTION_BASELINE[emotion_name]:

                state[emotion_name] += rate


            state[emotion_name] = max(
                0,
                min(
                    100,
                    state[emotion_name]
                )
            )


    save_emotion(emotion)


def analyze_emotion(message):


    msg = message.lower()


    if any(
        word in msg
        for word in [
            "nervous",
            "stress",
            "afraid",
            "scared",
            "anxious"
        ]
    ):

        return {
            "emotion": "anxiety",
            "intensity": 70
        }



    if any(
        word in msg
        for word in [
            "happy",
            "excited",
            "proud",
            "joy"
        ]
    ):

        return {
            "emotion": "happiness",
            "intensity": 80
        }



    if any(
        word in msg
        for word in [
            "sad",
            "lonely",
            "upset"
        ]
    ):

        return {
            "emotion": "sadness",
            "intensity": 70
        }



    return None