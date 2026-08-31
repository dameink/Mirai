from datetime import datetime
import re


# =====================================
# TEXT SIMILARITY
# =====================================


def normalize(text):

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        "",
        text
    )

    return set(
        text.split()
    )



def similarity(a, b):

    a_words = normalize(a)
    b_words = normalize(b)

    if not a_words or not b_words:
        return 0


    return (
        len(a_words & b_words)
        /
        len(a_words | b_words)
    )



# =====================================
# CHECK DUPLICATE
# =====================================


def is_duplicate(
        new_memory,
        old_memory
):

    return similarity(
        new_memory["content"],
        old_memory["content"]
    ) > 0.6





# =====================================
# CHECK CONFLICT
# =====================================


def is_conflict(
        new_memory,
        old_memory
):


    if new_memory.get("category") != old_memory.get("category"):

        return False



    new_text = new_memory["content"].lower()

    old_text = old_memory["content"].lower()



    # goals / preferences change


    negative_words = [
        "don't",
        "not",
        "no longer",
        "changed",
        "anymore"
    ]


    for word in negative_words:

        if word in new_text:

            return True



    if (
        "want to become" in new_text
        and
        "want to become" in old_text
    ):

        if similarity(
            new_text,
            old_text
        ) < 0.4:

            return True



    return False





# =====================================
# REINFORCE MEMORY
# =====================================


def reinforce_memory(memory):


    memory["confidence"] = min(

        100,

        memory.get(
            "confidence",
            50
        )
        +
        10

    )


    memory["recall_count"] = (

        memory.get(
            "recall_count",
            0
        )
        +
        1

    )


    memory["last_recalled"] = (
        datetime.now()
        .isoformat()
    )





# =====================================
# UPDATE MEMORY
# =====================================


def update_memory(
        old,
        new
):


    old["previous_versions"] = (
        old.get(
            "previous_versions",
            []
        )
    )


    old["previous_versions"].append({

        "content":
        old["content"],

        "date":
        datetime.now()
        .isoformat()

    })



    old["content"] = new["content"]


    old["confidence"] = min(

        100,

        old.get(
            "confidence",
            50
        )
        +
        15

    )


    old["last_updated"] = (
        datetime.now()
        .isoformat()
    )





# =====================================
# MAIN MERGE
# =====================================


def merge_memory(
        new_memory,
        memories
):


    for old_memory in memories:

                # conflict

        if is_conflict(
            new_memory,
            old_memory
        ):


            update_memory(
                old_memory,
                new_memory
            )


            return {

                "action":
                "updated",

                "memory":
                old_memory

            }


        # duplicate

        if is_duplicate(
            new_memory,
            old_memory
        ):


            reinforce_memory(
                old_memory
            )


            return {

                "action":
                "reinforced",

                "memory":
                old_memory

            }





    # completely new

    memories.append(
        new_memory
    )


    return {

        "action":
        "created",

        "memory":
        new_memory

    }