import json
from typing import Optional

from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db.database import get_db

from core.mirai import chat as mirai_chat

from core.emotion import get_emotion, reset_emotion
from core.relationship import get_relationship, reset_relationship

from core.learning import create_learning_context
from contextlib import asynccontextmanager
from db.init_db import init_db

from core.conversation import (
    load_conversation,
    clear_conversation,
)

from core.memory import clear_memory

from auth.router import router as auth_router
from auth.router import get_current_user
from notifications.router import router as notifications_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
app = FastAPI(
    title="Mirai API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(notifications_router)


# =========================================
# REQUEST MODELS
# =========================================

class ChatRequest(BaseModel):
    message: str
    language: Optional[str] = None
    mode: Optional[str] = None


# =========================================
# HOME
# =========================================

@app.get("/")
def home():
    return {
        "message": "Mirai is alive!"
    }


# =========================================
# CHAT
# =========================================

@app.post("/chat")
def chat_endpoint(
    request: ChatRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = mirai_chat(
        request.message,
        language=request.language,
        mode=request.mode,
        user_id=current_user["id"],
        db=db,
    )

    return result


# =========================================
# CONVERSATION
# =========================================

@app.get("/conversation")
def conversation(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = current_user["id"]

    return load_conversation(
        user_id=user_id,
        db=db,
    )


@app.delete("/conversation")
def delete_conversation(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = current_user["id"]

    clear_conversation(
        user_id=user_id,
        db=db,
    )

    return {
        "message": "Conversation cleared"
    }


# =========================================
# STATE
# =========================================

@app.get("/state")
def state(
    current_user=Depends(get_current_user),
):
    user_id = current_user["id"]

    learning_context = create_learning_context(user_id)

    return {
        "emotion": get_emotion(
            user_id=user_id,
        )["state"],

        "relationship": get_relationship(
            user_id=user_id,
        ),

        "learning": learning_context.learning.get_profile(),
    }


# =========================================
# LEARNING PROFILE
# =========================================

@app.get("/learning/profile")
def learning_profile(
    current_user=Depends(get_current_user),
):
    user_id = current_user["id"]

    learning_context = create_learning_context(user_id)

    return learning_context.learning.get_profile()


# =========================================
# LEARNING STRATEGY
# =========================================

@app.get("/learning/strategy")
def learning_strategy(
    current_user=Depends(get_current_user),
):
    user_id = current_user["id"]

    learning_context = create_learning_context(user_id)

    return learning_context.learning.get_strategy()


# =========================================
# LEARNING HISTORY
# =========================================

@app.get("/learning/history")
def learning_history(
    current_user=Depends(get_current_user),
):
    user_id = current_user["id"]

    learning_context = create_learning_context(user_id)

    return learning_context.learning.get_history()


# =========================================
# LEARNING MEMORY
# =========================================

@app.get("/learning/memory")
def learning_memory(
    current_user=Depends(get_current_user),
):
    user_id = current_user["id"]

    learning_context = create_learning_context(user_id)

    return learning_context.learning.get_learning_memory()


# =========================================
# LEARNING ANALYSIS
# =========================================

@app.get("/learning/analysis")
def learning_analysis(
    current_user=Depends(get_current_user),
):
    user_id = current_user["id"]

    learning_context = create_learning_context(user_id)

    return learning_context.learning.get_memory_analysis()


# =========================================
# START LEARNING SESSION
# =========================================

@app.post("/learning/session/start")
def start_learning_session(
    current_user=Depends(get_current_user),
):
    user_id = current_user["id"]

    learning_context = create_learning_context(user_id)

    session = learning_context.learning.start_learning()

    return {
        "session": session
    }


# =========================================
# FULL RESET
# =========================================

@app.delete("/reset")
def full_reset(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = current_user["id"]

    # -------------------------------------
    # Conversation
    # -------------------------------------

    clear_conversation(
        user_id=user_id,
        db=db,
    )

    # -------------------------------------
    # Memory
    # -------------------------------------

    clear_memory(
        user_id=user_id,
        db=db,
    )

    # -------------------------------------
    # Emotion
    # -------------------------------------

    reset_emotion(
        user_id=user_id,
    )

    # -------------------------------------
    # Relationship
    # -------------------------------------

    reset_relationship(
        user_id=user_id,
    )

    # -------------------------------------
    # Learning
    # -------------------------------------

    learning_context = create_learning_context(user_id)
    learning_context.learning.learner.reset()

    return {
        "message": "Mirai fully reset"
    }