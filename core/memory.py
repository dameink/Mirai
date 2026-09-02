import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from db.models import Memory, EmotionalMemory
from core.memory_merge import merge_memory


# ============================================
# TIME
# ============================================

def _now():
    return datetime.now(timezone.utc)


# ============================================
# DEFAULT MEMORY
# ============================================

def create_default_memory():
    return {
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
    }


# ============================================
# MEMORY OBJECT
# ============================================

def create_memory(
    content,
    importance=50,
    category="general",
    emotion=None
):
    return {
        "content": content,
        "importance": importance,
        "category": category,
        "created": _now().isoformat(),
        "last_recalled": None,
        "recall_count": 0,
        "emotion": emotion,
        "confidence": 50
    }


# ============================================
# DB → DICT
# ============================================

def _memory_to_dict(memory):
    return {
        "id": memory.id,
        "content": memory.content,
        "importance": memory.importance,
        "category": memory.category,
        "created": (
            memory.created_at.isoformat()
            if memory.created_at
            else None
        ),
        "last_recalled": (
            memory.last_recalled.isoformat()
            if memory.last_recalled
            else None
        ),
        "recall_count": memory.recall_count or 0,
        "emotion": memory.emotion,
        "confidence": memory.confidence or 50,
    }


def _emotional_memory_to_dict(memory):
    return {
        "id": memory.id,
        "emotion": memory.emotion,
        "trigger": memory.trigger,
        "intensity": memory.intensity,
        "created": (
            memory.created_at.isoformat()
            if memory.created_at
            else None
        ),
    }


# ============================================
# GET MEMORY
# ============================================

def get_memory(
    user_id=None,
    db=None
):
    """
    Return the user's complete memory structure.

    Relationship state is intentionally NOT stored here.
    Relationship has its own system.
    """

    if db is None:
        raise ValueError("db is required")

    if not user_id:
        raise ValueError("user_id is required")

    semantic_rows = (
        db.query(Memory)
        .filter(
            Memory.user_id == user_id,
            Memory.memory_type == "semantic"
        )
        .order_by(Memory.created_at.asc())
        .all()
    )

    episodic_rows = (
        db.query(Memory)
        .filter(
            Memory.user_id == user_id,
            Memory.memory_type == "episodic"
        )
        .order_by(Memory.created_at.asc())
        .all()
    )

    emotional_rows = (
        db.query(EmotionalMemory)
        .filter(
            EmotionalMemory.user_id == user_id
        )
        .order_by(EmotionalMemory.created_at.asc())
        .all()
    )

    return {
        "semantic": {
            "facts": [
                _memory_to_dict(row)
                for row in semantic_rows
            ]
        },

        "episodic": {
            "events": [
                _memory_to_dict(row)
                for row in episodic_rows
            ]
        },

        "emotional": {
            "states": [
                _emotional_memory_to_dict(row)
                for row in emotional_rows
            ]
        },

        "relationship": {
            "trust": 0,
            "affection": 0,
            "familiarity": 0,
            "interaction_count": 0
        }
    }


# ============================================
# LOAD MEMORY
# ============================================

def load_memory(
    user_id=None,
    db=None
):
    """
    Compatibility wrapper for the old JSON API.
    """

    return get_memory(
        user_id=user_id,
        db=db
    )


# ============================================
# SAVE MEMORY
# ============================================

def save_memory(
    memory,
    user_id=None,
    db=None
):
    """
    Compatibility function.

    Memory is now persisted through explicit DB
    operations. This function intentionally does
    not rewrite the whole memory structure.
    """

    if db is None:
        raise ValueError("db is required")

    if not user_id:
        raise ValueError("user_id is required")

    return memory


# ============================================
# SEMANTIC MEMORY
# ============================================

def remember_semantic(
    content,
    importance=50,
    category="general",
    emotion=None,
    user_id=None,
    db=None
):
    """
    Store semantic memory using memory_merge.

    Actions:
        created
        updated
        reinforced
    """

    if db is None:
        raise ValueError("db is required")

    if not user_id:
        raise ValueError("user_id is required")

    existing_rows = (
        db.query(Memory)
        .filter(
            Memory.user_id == user_id,
            Memory.memory_type == "semantic"
        )
        .order_by(Memory.created_at.asc())
        .all()
    )

    facts = [
        _memory_to_dict(row)
        for row in existing_rows
    ]

    new_memory = create_memory(
        content=content,
        importance=importance,
        category=category,
        emotion=emotion
    )

    result = merge_memory(
        new_memory,
        facts
    )

    action = result.get("action")
    merged_memory = result.get("memory")

    if not merged_memory:
        return result

    # ----------------------------------------
    # CREATED
    # ----------------------------------------

    if action == "created":

        row = Memory(
            id=str(uuid.uuid4()),
            user_id=user_id,
            memory_type="semantic",
            content=merged_memory.get(
                "content",
                content
            ),
            importance=merged_memory.get(
                "importance",
                importance
            ),
            category=merged_memory.get(
                "category",
                category
            ),
            emotion=merged_memory.get(
                "emotion",
                emotion
            ),
            confidence=merged_memory.get(
                "confidence",
                50
            ),
            recall_count=merged_memory.get(
                "recall_count",
                0
            ),
            created_at=_now(),
            last_recalled=None
        )

        db.add(row)
        db.commit()
        db.refresh(row)

        return {
            "action": "created",
            "memory": _memory_to_dict(row)
        }

    # ----------------------------------------
    # UPDATED / REINFORCED
    # ----------------------------------------

    if action in {
        "updated",
        "reinforced"
    }:

        memory_id = merged_memory.get("id")

        row = None

        # First try by ID.
        if memory_id:
            row = (
                db.query(Memory)
                .filter(
                    Memory.id == memory_id,
                    Memory.user_id == user_id,
                    Memory.memory_type == "semantic"
                )
                .first()
            )

        # Compatibility fallback for old
        # memories that might not have an ID.
        if row is None:

            old_content = merged_memory.get(
                "content"
            )

            if old_content:

                row = (
                    db.query(Memory)
                    .filter(
                        Memory.user_id == user_id,
                        Memory.memory_type == "semantic",
                        Memory.content == old_content
                    )
                    .first()
                )

        if row is None:
            raise RuntimeError(
                "Merged memory could not be matched to DB row."
            )

        # Update fields produced by merge_memory.

        row.content = merged_memory.get(
            "content",
            row.content
        )

        row.importance = merged_memory.get(
            "importance",
            row.importance
        )

        row.category = merged_memory.get(
            "category",
            row.category
        )

        row.emotion = merged_memory.get(
            "emotion",
            row.emotion
        )

        row.confidence = merged_memory.get(
            "confidence",
            row.confidence
        )

        row.recall_count = merged_memory.get(
            "recall_count",
            row.recall_count
        )

        if merged_memory.get("last_recalled"):
            try:
                row.last_recalled = (
                    datetime.fromisoformat(
                        merged_memory[
                            "last_recalled"
                        ]
                    )
                )
            except (
                ValueError,
                TypeError
            ):
                pass

        db.commit()
        db.refresh(row)

        return {
            "action": action,
            "memory": _memory_to_dict(row)
        }

    db.commit()

    return result


# ============================================
# RECALL SEMANTIC
# ============================================

def recall_semantic(
    keyword,
    user_id=None,
    db=None
):
    """
    Search semantic memory and reinforce
    recalled memories.
    """

    if db is None:
        raise ValueError("db is required")

    if not user_id:
        raise ValueError("user_id is required")

    keyword = (
        keyword or ""
    ).lower().strip()

    if not keyword:
        return []

    rows = (
        db.query(Memory)
        .filter(
            Memory.user_id == user_id,
            Memory.memory_type == "semantic"
        )
        .all()
    )

    results = []

    for row in rows:

        content = row.content or ""

        if keyword in content.lower():

            row.recall_count = (
                row.recall_count or 0
            ) + 1

            row.last_recalled = _now()

            row.confidence = min(
                100,
                (row.confidence or 50) + 5
            )

            results.append(
                _memory_to_dict(row)
            )

    db.commit()

    return results


# ============================================
# SEARCH SEMANTIC
# ============================================

def search_semantic(
    keyword,
    user_id=None,
    db=None
):
    """
    Search semantic memory without
    modifying recall metadata.
    """

    if db is None:
        raise ValueError("db is required")

    if not user_id:
        raise ValueError("user_id is required")

    keyword = (
        keyword or ""
    ).lower().strip()

    if not keyword:
        return []

    rows = (
        db.query(Memory)
        .filter(
            Memory.user_id == user_id,
            Memory.memory_type == "semantic"
        )
        .all()
    )

    return [
        _memory_to_dict(row)
        for row in rows
        if keyword in (
            row.content or ""
        ).lower()
    ]


# ============================================
# EPISODIC MEMORY
# ============================================

def remember_event(
    content,
    importance=50,
    user_id=None,
    db=None
):
    if db is None:
        raise ValueError("db is required")

    if not user_id:
        raise ValueError("user_id is required")

    row = Memory(
        id=str(uuid.uuid4()),
        user_id=user_id,
        memory_type="episodic",
        content=content,
        importance=importance,
        category="event",
        emotion=None,
        confidence=50,
        recall_count=0,
        created_at=_now(),
        last_recalled=None
    )

    db.add(row)
    db.commit()
    db.refresh(row)

    return _memory_to_dict(row)


# ============================================
# EMOTIONAL MEMORY
# ============================================

def remember_emotion(
    emotion,
    trigger,
    intensity=50,
    user_id=None,
    db=None
):
    if db is None:
        raise ValueError("db is required")

    if not user_id:
        raise ValueError("user_id is required")

    row = EmotionalMemory(
        id=str(uuid.uuid4()),
        user_id=user_id,
        emotion=emotion,
        trigger=trigger,
        intensity=intensity,
        created_at=_now()
    )

    db.add(row)
    db.commit()
    db.refresh(row)

    return _emotional_memory_to_dict(row)


# ============================================
# CLEAR MEMORY
# ============================================

def clear_memory(
    user_id=None,
    db=None
):
    if db is None:
        raise ValueError("db is required")

    if not user_id:
        raise ValueError("user_id is required")

    db.query(Memory).filter(
        Memory.user_id == user_id
    ).delete(
        synchronize_session=False
    )

    db.query(EmotionalMemory).filter(
        EmotionalMemory.user_id == user_id
    ).delete(
        synchronize_session=False
    )

    db.commit()

    return create_default_memory()


# ============================================
# FORGET SEMANTIC
# ============================================

def forget_semantic(
    keyword,
    user_id=None,
    db=None
):
    if db is None:
        raise ValueError("db is required")

    if not user_id:
        raise ValueError("user_id is required")

    keyword = (
        keyword or ""
    ).lower().strip()

    if not keyword:
        return False

    rows = (
        db.query(Memory)
        .filter(
            Memory.user_id == user_id,
            Memory.memory_type == "semantic"
        )
        .all()
    )

    to_delete = [
        row
        for row in rows
        if keyword in (
            row.content or ""
        ).lower()
    ]

    if not to_delete:
        return False

    for row in to_delete:
        db.delete(row)

    db.commit()

    return True