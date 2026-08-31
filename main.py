from fastapi import FastAPI
from pydantic import BaseModel
import json

from core.mirai import chat
from core.emotion import get_emotion
from core.learning import learning_context


app = FastAPI()


class ChatRequest(BaseModel):
    message: str


# =================================
# HOME
# =================================

@app.get("/")
def home():
    return {
        "message": "Mirai is alive!"
    }


# =================================
# CHAT
# =================================

@app.post("/chat")
def chat_endpoint(request: ChatRequest):

    result = chat(request.message)

    return {
        "mirai": result["response"],
        "state": result["state"]
    }


# =================================
# CONVERSATION
# =================================

@app.get("/conversation")
def conversation():

    with open(
        "conversation.json",
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


@app.delete("/conversation")
def delete_conversation():

    with open(
        "conversation.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            [],
            file,
            indent=4
        )

    return {
        "message": "Conversation cleared"
    }


# =================================
# STATE
# =================================

@app.get("/state")
def state():

    with open(
        "relationship.json",
        "r",
        encoding="utf-8"
    ) as file:

        relationship = json.load(file)

    emotion = get_emotion()

    learning = learning_context.learning

    return {
        "emotion": emotion["state"],
        "relationship": relationship,
        "learning": learning.get_profile()
    }


# =================================
# LEARNING PROFILE
# =================================

@app.get("/learning/profile")
def learning_profile():

    return learning_context.learning.get_profile()


# =================================
# LEARNING STRATEGY
# =================================

@app.get("/learning/strategy")
def learning_strategy():

    return learning_context.learning.get_strategy()


# =================================
# LEARNING HISTORY
# =================================

@app.get("/learning/history")
def learning_history():

    return learning_context.learning.get_history()


# =================================
# LEARNING MEMORY
# =================================

@app.get("/learning/memory")
def learning_memory():

    return learning_context.learning.get_learning_memory()


# =================================
# LEARNING ANALYSIS
# =================================

@app.get("/learning/analysis")
def learning_analysis():

    return learning_context.learning.get_memory_analysis()


# =================================
# START LEARNING SESSION
# =================================

@app.post("/learning/session/start")
def start_learning_session():

    session = learning_context.learning.start_learning()

    return {
        "session": session
    }


# =================================
# FULL RESET
# =================================

@app.delete("/reset")
def full_reset():

    # =================================
    # 1. Conversation
    # =================================

    with open(
        "conversation.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            [],
            file,
            indent=4
        )

    # =================================
    # 2. Memory
    # =================================

    with open(
        "memory.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            {
                "semantic": {
                    "facts": []
                },
                "episodic": {
                    "events": []
                },
                "emotional": {
                    "states": []
                },
                "relationship": {
                    "trust": 0,
                    "affection": 0,
                    "familiarity": 0,
                    "interaction_count": 0
                }
            },
            file,
            indent=4,
            ensure_ascii=False
        )

    # =================================
    # 3. Emotion
    # =================================

    with open(
        "emotion.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            {
                "state": {
                    "happiness": 70,
                    "energy": 80,
                    "trust": 50,
                    "curiosity": 80,
                    "comfort": 60,
                    "excitement": 50,
                    "stress": 20
                }
            },
            file,
            indent=4
        )

    # =================================
    # 4. Relationship
    # =================================

    with open(
        "relationship.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            {
                "stage": "stranger",
                "closeness": 0,
                "familiarity": 0,
                "bond": 20,
                "affection": 0,
                "respect": 50,
                "comfort": 50
            },
            file,
            indent=4
        )

    return {
        "message": "Mirai fully reset"
    }


    # =================================
    # 2. Learning memory
    # =================================

    with open(
        "memory.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            {
                "semantic": {
                    "facts": []
                },
                "episodic": {
                    "events": []
                },
                "emotional": {
                    "states": []
                },
                "relationship_memory": []
            },
            file,
            indent=4
        )


    # =================================
    # 3. Emotion
    # =================================

    with open(
        "emotion.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            {
                "state": {
                    "happiness": 70,
                    "energy": 80,
                    "trust": 50,
                    "curiosity": 80,
                    "comfort": 60,
                    "excitement": 50,
                    "stress": 20
                }
            },
            file,
            indent=4
        )


    # =================================
    # 4. Relationship
    # =================================

    with open(
        "relationship.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            {
                "stage": "stranger",
                "closeness": 0,
                "familiarity": 0.5,
                "bond": 20.0,
                "affection": 0,
                "respect": 50,
                "comfort": 50
            },
            file,
            indent=4
        )


    return {
        "message": "Mirai full reset completed"
    }