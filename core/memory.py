import json
import os
from datetime import datetime

from core.memory_merge import merge_memory


MEMORY_FILE = "memory.json"


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
        "created": datetime.now().isoformat(),
        "last_recalled": None,
        "recall_count": 0,
        "emotion": emotion,
        "confidence": 50
    }


# ============================================
# LOAD
# ============================================

def load_memory():
    """
    Load memory.json.

    If the file does not exist or is invalid,
    create a clean default memory.
    """

    if not os.path.exists(MEMORY_FILE):
        memory = create_default_memory()
        save_memory(memory)
        return memory

    try:
        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            memory = json.load(file)

    except (json.JSONDecodeError, OSError):
        memory = create_default_memory()
        save_memory(memory)
        return memory

    # ----------------------------------------
    # Repair missing sections
    # ----------------------------------------

    default = create_default_memory()

    for section in default:
        if section not in memory:
            memory[section] = default[section]

    for section in [
        "semantic",
        "episodic",
        "emotional"
    ]:
        if not isinstance(memory.get(section), dict):
            memory[section] = default[section]

    if not isinstance(
        memory["semantic"].get("facts"),
        list
    ):
        memory["semantic"]["facts"] = []

    if not isinstance(
        memory["episodic"].get("events"),
        list
    ):
        memory["episodic"]["events"] = []

    if not isinstance(
        memory["emotional"].get("states"),
        list
    ):
        memory["emotional"]["states"] = []

    if not isinstance(
        memory["relationship"],
        dict
    ):
        memory["relationship"] = default["relationship"]

    return memory


# ============================================
# SAVE
# ============================================

def save_memory(memory):
    """
    Save memory safely to JSON.
    """

    with open(
        MEMORY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            memory,
            file,
            indent=4,
            ensure_ascii=False
        )


# ============================================
# GET MEMORY
# ============================================

def get_memory():
    return load_memory()


# ============================================
# SEMANTIC MEMORY
# ============================================

def remember_semantic(
    content,
    importance=50,
    category="general",
    emotion=None
):
    """
    Store a semantic memory.

    merge_memory decides whether the memory is:
    - new
    - duplicate
    - conflicting
    """

    memory = load_memory()

    facts = memory["semantic"]["facts"]

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

    # merge_memory mutates `facts` directly.
    memory["semantic"]["facts"] = facts

    save_memory(memory)

    return result


# ============================================
# RECALL SEMANTIC MEMORY
# ============================================

def recall_semantic(keyword):
    """
    Search semantic memory and reinforce
    memories that are recalled.
    """

    memory = load_memory()

    results = []

    keyword = keyword.lower().strip()

    if not keyword:
        return results

    for fact in memory["semantic"]["facts"]:

        content = fact.get(
            "content",
            ""
        )

        if keyword in content.lower():

            fact["recall_count"] = (
                fact.get(
                    "recall_count",
                    0
                )
                + 1
            )

            fact["last_recalled"] = (
                datetime.now().isoformat()
            )

            fact["confidence"] = min(
                100,
                fact.get(
                    "confidence",
                    50
                ) + 5
            )

            results.append(fact)

    save_memory(memory)

    return results


# ============================================
# SEARCH
# ============================================

def search_semantic(keyword):
    """
    Search without modifying memories.
    """

    memory = load_memory()

    results = []

    keyword = keyword.lower().strip()

    if not keyword:
        return results

    for fact in memory["semantic"]["facts"]:

        content = fact.get(
            "content",
            ""
        )

        if keyword in content.lower():
            results.append(fact)

    return results


# ============================================
# EPISODIC MEMORY
# ============================================

def remember_event(
    content,
    importance=50
):
    memory = load_memory()

    event = create_memory(
        content=content,
        importance=importance,
        category="event"
    )

    memory["episodic"]["events"].append(
        event
    )

    save_memory(memory)

    return event


# ============================================
# EMOTIONAL MEMORY
# ============================================

def remember_emotion(
    emotion,
    trigger,
    intensity=50
):
    memory = load_memory()

    state = {
        "emotion": emotion,
        "trigger": trigger,
        "intensity": intensity,
        "created": datetime.now().isoformat()
    }

    memory["emotional"]["states"].append(
        state
    )

    save_memory(memory)

    return state


# ============================================
# RELATIONSHIP MEMORY
# ============================================

def update_relationship(
    trust=0,
    affection=0,
    familiarity=0
):
    memory = load_memory()

    relationship = memory["relationship"]

    relationship["trust"] += trust
    relationship["affection"] += affection
    relationship["familiarity"] += familiarity
    relationship["interaction_count"] += 1

    save_memory(memory)

    return relationship


# ============================================
# CLEAR
# ============================================

def clear_memory():
    memory = create_default_memory()

    save_memory(memory)

    return memory


# ============================================
# FORGET
# ============================================

def forget_semantic(keyword):
    memory = load_memory()

    facts = memory["semantic"]["facts"]

    keyword = keyword.lower().strip()

    if not keyword:
        return False

    original_count = len(facts)

    memory["semantic"]["facts"] = [
        fact
        for fact in facts
        if keyword not in fact.get(
            "content",
            ""
        ).lower()
    ]

    removed = (
        len(memory["semantic"]["facts"])
        < original_count
    )

    save_memory(memory)

    return removed