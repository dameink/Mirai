from core.memory import get_memory, save_memory
from datetime import datetime


# =====================================
# DECAY SETTINGS
# =====================================


BASE_DECAY = {

    "semantic": 0.05,

    "episodic": 0.08,

    "emotional": 0.15

}


MIN_STRENGTH = 5



# =====================================
# INITIALIZE MEMORY
# =====================================


def ensure_fields(memory):


    if "strength" not in memory:

        memory["strength"] = float(
            memory.get(
                "importance",
                50
            )
        )


    if "confidence" not in memory:

        memory["confidence"] = 50



    if "status" not in memory:

        memory["status"] = "active"



    if "last_decay" not in memory:

        memory["last_decay"] = (
            datetime.now()
            .isoformat()
        )





# =====================================
# DAYS PASSED
# =====================================


def days_since_decay(memory):


    try:

        last = datetime.fromisoformat(
            memory["last_decay"]
        )


        days = (
            datetime.now()
            -
            last
        ).days


        return max(
            days,
            1
        )


    except:


        return 1





# =====================================
# CALCULATE DECAY
# =====================================


def calculate_decay(
        memory,
        memory_type
):


    base = BASE_DECAY.get(
        memory_type,
        0.1
    )


    importance = memory.get(
        "importance",
        50
    )


    confidence = memory.get(
        "confidence",
        50
    )



    # важные воспоминания защищены

    importance_protection = (
        importance / 100
    )



    confidence_protection = (
        confidence / 200
    )



    protection = (
        importance_protection
        +
        confidence_protection
    )


    decay_multiplier = max(

        0.2,

        1 - protection

    )



    return (
        base
        *
        decay_multiplier
    )





# =====================================
# UPDATE STATUS
# =====================================


def update_status(memory):


    strength = memory.get(
        "strength",
        50
    )


    if strength >= 60:


        memory["status"] = "active"



    elif strength >= 25:


        memory["status"] = "weak"



    else:


        memory["status"] = "forgotten"





# =====================================
# APPLY DECAY TO ONE MEMORY
# =====================================


def decay_memory_item(
        memory,
        memory_type
):


    ensure_fields(
        memory
    )


    days = days_since_decay(
        memory
    )


    decay = calculate_decay(
        memory,
        memory_type
    )


    total_decay = (
        decay
        *
        days
    )



    memory["strength"] -= (
        total_decay
    )


    memory["strength"] = max(

        MIN_STRENGTH,

        round(
            memory["strength"],
            2
        )

    )



    # confidence follows strength


    if memory["strength"] < 30:


        memory["confidence"] = max(

            10,

            memory["confidence"] - 2

        )



    update_status(
        memory
    )



    memory["last_decay"] = (
        datetime.now()
        .isoformat()
    )





# =====================================
# APPLY DECAY TO ALL MEMORY
# =====================================


def apply_memory_decay(user_id=None):


    data = get_memory(user_id=user_id)



    memory_groups = {


        "semantic":
        data["semantic"]["facts"],



        "episodic":
        data["episodic"]["events"],



        "emotional":
        data["emotional"]["states"]

    }




    for memory_type, memories in memory_groups.items():


        for memory in memories:


            decay_memory_item(

                memory,

                memory_type

            )



    save_memory(
        data,
        user_id=user_id
    )


    return data





# =====================================
# STRENGTHEN MEMORY AFTER RECALL
# =====================================


def strengthen_memory(
        memory
):


    ensure_fields(
        memory
    )


    memory["strength"] += 5


    memory["strength"] = min(

        100,

        memory["strength"]

    )



    memory["confidence"] += 2


    memory["confidence"] = min(

        100,

        memory["confidence"]

    )



    memory["status"] = "active"



    memory["last_recalled"] = (
        datetime.now()
        .isoformat()
    )