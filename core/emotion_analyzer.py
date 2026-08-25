# core/emotion_analyzer.py


EMOTION_PATTERNS = {


    "happiness": {

        "words": [
            "happy",
            "proud",
            "excited",
            "great",
            "amazing",
            "love",
            "success",
            "finished"
        ],

        "intensity": 80
    },


    "anxiety": {

        "words": [
            "nervous",
            "stress",
            "worried",
            "afraid",
            "scared",
            "anxious"
        ],

        "intensity": 70
    },


    "sadness": {

        "words": [
            "sad",
            "lonely",
            "disappointed",
            "hurt"
        ],

        "intensity": 60
    },


    "frustration": {

        "words": [
            "angry",
            "annoyed",
            "frustrated",
            "hate"
        ],

        "intensity": 70
    }

}




def analyze_emotion(message):

    message = message.lower()


    for emotion, data in EMOTION_PATTERNS.items():

        for word in data["words"]:

            if word in message:

                return {

                    "emotion": emotion,

                    "intensity": data["intensity"]

                }


    return None