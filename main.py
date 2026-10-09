import json
import asyncio
import logging
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from db.models import ChatReceipt
import hashlib
from core.llm import LLMUnavailableError
from core.persistence import StateCorruptedError
from core.rate_limit import LIMITS, admit_request
from starlette.concurrency import run_in_threadpool
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from db.database import get_db
from db.init_db import init_db, check_schema
import os

from core.mirai import chat as mirai_chat
from core.personality import get_personality
from core.emotion import get_emotion, reset_emotion
from core.relationship import get_relationship, reset_relationship
from core.learning import create_learning_context

from core.conversation import (
    load_conversation,
    clear_conversation,
)

from core.memory import clear_memory

from auth.router import router as auth_router
from auth.router import get_current_user
from notifications.router import router as notifications_router

from gamification.router import router as gamification_router
from gamification.service import register_activity, unlock_achievement


# =========================================
# LIFESPAN
# =========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    from core.operations import validate_environment
    validate_environment()
    if os.getenv("MIRAI_AUTO_MIGRATE", "false").lower() == "true":
        init_db()
    else:
        check_schema()
    from auth.deletion import purge_deleted_files
    await run_in_threadpool(purge_deleted_files)
    async def retry_erasure():
        while True:
            await asyncio.sleep(60)
            try:
                await run_in_threadpool(purge_deleted_files)
            except Exception:
                logging.getLogger(__name__).error("Account erasure retry failed")
    worker = asyncio.create_task(retry_erasure())
    try:
        yield
    finally:
        worker.cancel()
        try:
            await worker
        except asyncio.CancelledError:
            pass


# =========================================
# APP
# =========================================

app = FastAPI(
    title="Mirai API",
    version="1.0.0",
    lifespan=lifespan,
)

@app.middleware("http")
async def limit_requests(request, call_next):
    if request.method in {"POST", "DELETE"} and request.url.path in LIMITS:
        identity = request.client.host if request.client else "unknown"
        allowed = await run_in_threadpool(admit_request, identity, request.url.path)
        if not allowed:
            return JSONResponse(status_code=429, content={"detail": "Too many requests. Please try again later."}, headers={"Retry-After": str(LIMITS[request.url.path][1])})
    return await call_next(request)


from db.unit_of_work import UserUnavailableError


@app.exception_handler(UserUnavailableError)
async def unavailable_user(request, error):
    return JSONResponse(status_code=401, content={"detail": "Session expired."})


@app.exception_handler(StateCorruptedError)
async def unavailable_state(request, error):
    return JSONResponse(status_code=503, content={"detail": "Your saved state is temporarily unavailable. Please contact support."})


@app.exception_handler(LLMUnavailableError)
async def unavailable_model(request, error):
    return JSONResponse(status_code=503, content={"detail": "Mirai is temporarily unavailable. Please try again."})


from core.operations import router as operations_router
from core.preferences import router as preferences_router
app.include_router(operations_router)
app.include_router(preferences_router)
app.include_router(auth_router)
app.include_router(notifications_router)
app.include_router(gamification_router)


# =========================================
# REQUEST MODELS
# =========================================

class ChatRequest(BaseModel):
    request_id: Optional[str] = Field(default=None, min_length=8, max_length=64)
    message: str = Field(min_length=1, max_length=4000)
    language: Optional[str] = Field(default=None, max_length=40)
    mode: Optional[str] = None

    @field_validator("message")
    @classmethod
    def nonempty_message(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Message cannot be blank")
        return value

    @field_validator("mode")
    @classmethod
    def valid_mode(cls, value):
        if value is not None and value not in {"Auto", "Casual", "Learning", "ACTIVE_LEARNING", "CASUAL_CONVERSATION"}:
            raise ValueError("Unknown conversation mode")
        return value


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
    current_user=Depends(get_current_user, scope="function"),
    db: Session = Depends(get_db),
):
    payload_hash = hashlib.sha256(json.dumps(
        request.model_dump(exclude={"request_id"}), sort_keys=True, ensure_ascii=False,
    ).encode()).hexdigest()
    if request.request_id:
        previous = db.get(ChatReceipt, (current_user["id"], request.request_id))
        if previous is not None:
            if previous.payload_hash != payload_hash:
                raise HTTPException(status_code=409, detail="Request ID was already used for a different message.")
            if previous.response is None:
                raise HTTPException(status_code=409, detail="This conversation was cleared. Send a new message.")
            return previous.response

    result = mirai_chat(
        request.message,
        language=request.language,
        mode=request.mode,
        user_id=current_user["id"],
        db=db,
    )

    # -------------------------------------
    # Gamification
    # -------------------------------------

    register_activity(
        db,
        current_user["id"],
        xp=10,
    )

    unlock_achievement(
        db,
        current_user["id"],
        "first_conversation",
    )

    result = jsonable_encoder(result)
    if request.request_id:
        db.add(ChatReceipt(user_id=current_user["id"], request_id=request.request_id,
                           payload_hash=payload_hash, response=result))
        db.flush()
    return result


# =========================================
# CONVERSATION
# =========================================

@app.get("/conversation")
def conversation(
    current_user=Depends(get_current_user, scope="function"),
    db: Session = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=100),
    before_id: Optional[str] = Query(default=None, max_length=36),
):
    return load_conversation(user_id=current_user["id"], db=db, limit=limit, before_id=before_id)


@app.delete("/conversation")
def delete_conversation(
    current_user=Depends(get_current_user, scope="function"),
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
    current_user=Depends(get_current_user, scope="function"),
):
    user_id = current_user["id"]

    # Learning
    learning_context = create_learning_context(user_id)

    return {
        "emotion": get_emotion(
            user_id=user_id,
        )["state"],

        "relationship": get_relationship(
            user_id=user_id,
        ),

        "personality": get_personality(),

        "learning": learning_context.learning.get_profile(),
    }


# =========================================
# LEARNING PROFILE
# =========================================

@app.get("/learning/profile")
def learning_profile(
    current_user=Depends(get_current_user, scope="function"),
):
    user_id = current_user["id"]

    learning_context = create_learning_context(user_id)

    return learning_context.learning.get_profile()


# =========================================
# LEARNING STRATEGY
# =========================================

@app.get("/learning/strategy")
def learning_strategy(
    current_user=Depends(get_current_user, scope="function"),
):
    user_id = current_user["id"]

    learning_context = create_learning_context(user_id)

    return learning_context.learning.get_strategy()


# =========================================
# LEARNING HISTORY
# =========================================

@app.get("/learning/history")
def learning_history(
    current_user=Depends(get_current_user, scope="function"),
):
    user_id = current_user["id"]

    learning_context = create_learning_context(user_id)

    return learning_context.learning.get_history()


# =========================================
# LEARNING MEMORY
# =========================================

@app.get("/learning/memory")
def learning_memory(
    current_user=Depends(get_current_user, scope="function"),
):
    user_id = current_user["id"]

    learning_context = create_learning_context(user_id)

    return learning_context.learning.get_learning_memory()


# =========================================
# LEARNING ANALYSIS
# =========================================

@app.get("/learning/analysis")
def learning_analysis(
    current_user=Depends(get_current_user, scope="function"),
):
    user_id = current_user["id"]

    learning_context = create_learning_context(user_id)

    return learning_context.learning.get_memory_analysis()


# =========================================
# START LEARNING SESSION
# =========================================

@app.post("/learning/session/start")
def start_learning_session(
    current_user=Depends(get_current_user, scope="function"),
):
    user_id = current_user["id"]

    learning_context = create_learning_context(user_id)

    session = learning_context.learning.start_learning()

    return {
        "session": session
    }


@app.post("/learning/session/{session_id}/complete")
def complete_learning_session(session_id: str, current_user=Depends(get_current_user, scope="function")):
    context = create_learning_context(current_user["id"])
    controller = context.learning.learning
    session = controller.get_last_session()
    if session is None or session.id != session_id:
        raise HTTPException(status_code=404, detail="Practice session not found.")
    if session.completed:
        return {"session": session.get_data()}
    if session.message_count < 1:
        raise HTTPException(status_code=409, detail="Send a message in practice before finishing.")
    # Conversation evidence is already recorded by the chat pipeline. Do not invent scores.
    session.complete(result={}, improvements={})
    controller.sessions.save()
    return {"session": session.get_data()}


# =========================================
# FULL RESET
# =========================================

@app.delete("/reset")
def full_reset(
    current_user=Depends(get_current_user, scope="function"),
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

@app.get('/chat/requests/{request_id}')
def chat_request_status(request_id: str, user=Depends(get_current_user, scope='function'), db: Session = Depends(get_db)):
    receipt = db.get(ChatReceipt, (user['id'], request_id))
    if receipt is None: return {'status': 'unknown'}
    return {'status': 'cleared' if receipt.response is None else 'completed'}
