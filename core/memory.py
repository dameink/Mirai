import json
import os
from datetime import datetime
from core.memory_merge import merge_memory


MEMORY_FILE = "memory.json"



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

        "created":
        datetime.now().isoformat(),

        "last_recalled": None,

        "recall_count": 0,

        "emotion": emotion,

        "confidence": 50

    }



def load_memory():

    if not os.path.exists(MEMORY_FILE):

        memory = create_default_memory()

        save_memory(memory)

        return memory


    with open(MEMORY_FILE, "r") as file:

        return json.load(file)



def save_memory(memory):

    with open(MEMORY_FILE, "w") as file:

        json.dump(
            memory,
            file,
            indent=4
        )



def get_memory():

    return load_memory()



# =========================
# SEMANTIC MEMORY
# ========================


def remember_semantic(
        content,
        importance=50,
        category="general",
        emotion=None
):

    memory = load_memory()


    facts = memory["semantic"]["facts"]


    new_memory = create_memory(
        content,
        importance,
        category,
        emotion
    )


    result = merge_memory(
        new_memory,
        facts
    )


    save_memory(memory)


    return result



# =========================
# EPISODIC MEMORY
# =========================


def remember_event(
        content,
        importance=50
):

    memory = load_memory()


    event = create_memory(
        content,
        importance,
        "event"
    )


    memory["episodic"]["events"].append(event)


    save_memory(memory)



# =========================
# EMOTIONAL MEMORY
# =========================


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

        "created":
        datetime.now().isoformat()

    }


    memory["emotional"]["states"].append(state)


    save_memory(memory)



# =========================
# RELATIONSHIP MEMORY
# =========================


def update_relationship(
        trust=0,
        affection=0,
        familiarity=0
):

    memory = load_memory()


    relation = memory["relationship"]


    relation["trust"] += trust

    relation["affection"] += affection

    relation["familiarity"] += familiarity

    relation["interaction_count"] += 1


    save_memory(memory)



# =========================
# SEARCH
# =========================


def search_semantic(keyword):

    memory = load_memory()


    results=[]


    for fact in memory["semantic"]["facts"]:

        if keyword.lower() in fact["content"].lower():

            results.append(fact)


    return results



# =========================
# CLEAR
# =========================


def clear_memory():

    save_memory(
        create_default_memory()
    )

# =========================
# FORGET SEMANTIC MEMORY
# =========================

def forget_semantic(keyword):

    memory = load_memory()

    facts = memory["semantic"]["facts"]

    new_facts = []

    removed = False

    for fact in facts:

        if keyword.lower() in fact["content"].lower():

            removed = True
            continue

        new_facts.append(fact)


    memory["semantic"]["facts"] = new_facts

    save_memory(memory)

    return removed