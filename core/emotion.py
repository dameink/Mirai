import json
import os

from core.user_state import get_user_file


EMOTION_FILE = "emotion.json"


DEFAULT_EMOTION = {
    "state": {
        "happiness": 70,
        "energy": 80,
        "trust": 50,
        "curiosity": 80,
        "comfort": 60,
        "excitement": 50,
        "stress": 20,
    },
    "emotional_style": {
        "expressiveness": 75,
        "sensitivity": 60,
        "recovery_speed": 80,
    },
}


EMOTION_BASELINE = {
    "happiness": 70,
    "energy": 80,
    "trust": 50,
    "curiosity": 80,
    "comfort": 60,
    "excitement": 50,
    "stress": 20,
}


def _emotion_file(user_id=None):
    if user_id:
        return get_user_file(user_id, EMOTION_FILE)

    return EMOTION_FILE


def load_emotion(user_id=None):
    emotion_file = _emotion_file(user_id)

    if not os.path.exists(emotion_file):
        save_emotion(DEFAULT_EMOTION, user_id=user_id)
        return DEFAULT_EMOTION.copy()

    try:
        with open(
            emotion_file,
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    except json.JSONDecodeError:
        save_emotion(DEFAULT_EMOTION, user_id=user_id)
        return DEFAULT_EMOTION.copy()


def save_emotion(emotion, user_id=None):
    emotion_file = _emotion_file(user_id)

    os.makedirs(
        os.path.dirname(emotion_file) or ".",
        exist_ok=True,
    )

    with open(
        emotion_file,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            emotion,
            file,
            indent=4,
            ensure_ascii=False,
        )


def change_emotion(
    emotion_name,
    amount,
    user_id=None,
    db=None,
):
    emotion = load_emotion(user_id=user_id)

    if emotion_name in emotion["state"]:
        emotion["state"][emotion_name] += amount

        emotion["state"][emotion_name] = max(
            0,
            min(
                100,
                emotion["state"][emotion_name],
            ),
        )

    save_emotion(
        emotion,
        user_id=user_id,
    )


def get_emotion(user_id=None, db=None):
    return load_emotion(user_id=user_id)


def reset_emotion(user_id=None):
    save_emotion(
        DEFAULT_EMOTION,
        user_id=user_id,
    )


def emotional_reaction(user_id=None):
    emotion = load_emotion(user_id=user_id)

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


def decay_emotions(user_id=None):
    emotion = load_emotion(user_id=user_id)

    state = emotion["state"]

    decay_rates = {
        "happiness": 1,
        "energy": 1,
        "curiosity": 1,
        "comfort": 0.5,
        "excitement": 1,
        "stress": 1,
        "trust": 0.2,
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
                    state[emotion_name],
                ),
            )

    save_emotion(
        emotion,
        user_id=user_id,
    )


def analyze_emotion(message):
    msg = message.lower()

    if any(
        word in msg
        for word in [
            "nervous",
            "stress",
            "afraid",
            "scared",
            "anxious",
        ]
    ):
        return {
            "emotion": "anxiety",
            "intensity": 70,
        }

    if any(
        word in msg
        for word in [
            "happy",
            "excited",
            "proud",
            "joy",
        ]
    ):
        return {
            "emotion": "happiness",
            "intensity": 80,
        }

    if any(
        word in msg
        for word in [
            "sad",
            "lonely",
            "upset",
        ]
    ):
        return {
            "emotion": "sadness",
            "intensity": 70,
        }

    return None