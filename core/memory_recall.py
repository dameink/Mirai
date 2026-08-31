from core.memory import get_memory, save_memory
from datetime import datetime
import re


# =====================================
# MEMORY TYPE WEIGHTS
# =====================================

TYPE_WEIGHT = {

    "semantic": 1.0,

    "episodic": 1.15,

    "emotional": 1.25,

    "relationship": 1.2

}



# =====================================
# SYNONYMS
# =====================================

SYNONYMS = {


    "career": [
        "goal",
        "future",
        "profession",
        "job",
        "dream",
        "ambition"
    ],


    "goal": [
        "want",
        "plan",
        "future",
        "dream",
        "aim",
        "target"
    ],


    "project": [
        "building",
        "creating",
        "application",
        "app",
        "working",
        "developing"
    ],


    "achievement": [
        "passed",
        "success",
        "finished",
        "completed",
        "accomplished"
    ],


    "interest": [
        "like",
        "love",
        "enjoy",
        "hobby",
        "favorite",
        "passion"
    ],


    "emotion": [
        "feel",
        "feeling",
        "mood",
        "state"
    ],


    "started": [
        "began",
        "created",
        "initial",
        "first",
        "origin"
    ],


    "remember": [
        "recall",
        "before",
        "past",
        "previous"
    ]

}



# =====================================
# CONTEXT FILTER
# =====================================

ALLOWED_MEMORY_TYPES = {


    "goal": [

        "semantic",
        "episodic"

    ],


    "project": [

        "semantic",
        "episodic"

    ],


    "interest": [

        "semantic"

    ],


    "achievement": [

        "semantic",
        "episodic"

    ],


    "emotion": [

        "emotional",
        "episodic",
        "relationship"

    ],


    None: [

        "semantic",
        "episodic",
        "emotional",
        "relationship"

    ]

}





# =====================================
# TEXT PROCESSING
# =====================================


def normalize_text(text):

    text = text.lower()


    text = re.sub(
        r"[^a-z0-9\s]",
        "",
        text
    )


    return set(
        text.split()
    )





def expand_words(words):

    expanded = set(words)


    for word in words:


        for key, values in SYNONYMS.items():


            if word == key:

                expanded.update(values)


            if word in values:

                expanded.add(key)


    return expanded





def similarity(message, content):


    message_words = expand_words(
        normalize_text(message)
    )


    content_words = expand_words(
        normalize_text(content)
    )


    if not message_words:

        return 0



    common = (
        message_words
        &
        content_words
    )


    return (
        len(common)
        /
        len(message_words)
    ) * 100





# =====================================
# CONTEXT FALLBACK
# =====================================


def detect_context(message):


    msg = message.lower()



    if any(x in msg for x in [
        "goal",
        "career",
        "future",
        "want",
        "dream",
        "plan",
        "profession"
    ]):

        return "goal"



    if any(x in msg for x in [
        "project",
        "building",
        "working",
        "creating",
        "application"
    ]):

        return "project"



    if any(x in msg for x in [
        "achievement",
        "success",
        "passed",
        "completed"
    ]):

        return "achievement"



    if any(x in msg for x in [
        "like",
        "love",
        "interest",
        "hobby",
        "enjoy"
    ]):

        return "interest"



    if any(x in msg for x in [
        "feel",
        "nervous",
        "stress",
        "sad",
        "happy",
        "afraid",
        "lonely"
    ]):

        return "emotion"



    return None





# =====================================
# CATEGORY SCORE
# =====================================


def category_bonus(
        message,
        memory,
        context=None
):


    if context is None:

        context = detect_context(
            message
        )


    category = memory.get(
        "category",
        ""
    )


    mapping = {


        "goal": {

            "goal":80

        },


        "project": {

            "project":80

        },


        "achievement": {

            "achievement":70

        },


        "interest": {

            "interest":70

        },


        "emotion": {

            "emotion":80,
            "stress":60

        }

    }

    if category == "personal":
        msg = message.lower()
        content = memory.get("content", "").lower()

        if "my name" in msg and "user name" in content:
            return 80


    return mapping.get(
        context,
        {}
    ).get(
        category,
        0
    )


# =====================================
# CATEGORY PENALTY
# =====================================


def category_penalty(
        message,
        memory
):


    context = detect_context(
        message
    )


    category = memory.get(
        "category",
        ""
    )


    penalties = {


        "goal": [
            "interest",
            "project",
            "achievement"
        ],


        "interest": [
            "goal",
            "achievement",
            "project"
        ],


        "project": [
            "goal",
            "interest",
            "achievement"
        ],


        "achievement": [
            "goal",
            "interest"
        ],


        "emotion": [
            "goal",
            "project",
            "interest"
        ]

    }


    if context in penalties:

        if category in penalties[context]:

            return -40


    return 0



# =====================================
# EMOTION MATCH
# =====================================


def emotion_bonus(
        message,
        memory,
        context=None
):


    if context is None:

        context = detect_context(
            message
        )


    if context != "emotion":

        return -30



    msg = message.lower()


    emotion = memory.get(
        "emotion"
    )


    if emotion == "anxiety":

        if any(x in msg for x in [
            "nervous",
            "stress",
            "afraid"
        ]):

            return 80



    if emotion == "happiness":

        if any(x in msg for x in [
            "happy",
            "proud",
            "excited"
        ]):

            return 70



    return 0





# =====================================
# TIME
# =====================================


def recency(memory):


    created = memory.get(
        "created"
    )


    if not created:

        return 5



    try:

        date = datetime.fromisoformat(
            created
        )


        days = (
            datetime.now()
            -
            date
        ).days


        return max(
            0,
            20 - days * 0.05
        )


    except:

        return 5





# =====================================
# SCORE
# =====================================


def calculate_score(
        message,
        memory,
        memory_type,
        context=None
):


    content = memory.get(
        "content",
        memory.get(
            "trigger",
            ""
        )
    )


    score = 0


    score += similarity(
        message,
        content
    ) * 0.4



    score += memory.get(
        "importance",
        50
    ) * 0.2



    score += memory.get(
        "confidence",
        50
    ) * 0.15



    score += memory.get(
        "recall_count",
        0
    ) * 2



    score += recency(
        memory
    )



    score += category_bonus(
        message,
        memory,
        context
    )

    score += category_penalty(
        message,
        memory
    )



    score += emotion_bonus(
        message,
        memory,
        context
    )



    score *= TYPE_WEIGHT.get(
        memory_type,
        1
    )



    return round(
        score,
        2
    )





# =====================================
# MAIN RECALL
# =====================================


def recall_memory(
        message,
        limit=5,
        cognition=None
):


    data = get_memory()


    results = []



    if cognition:

        context = cognition.get(
            "context"
        )

    else:

        context = detect_context(
            message
        )



    allowed = ALLOWED_MEMORY_TYPES.get(
        context,
        ALLOWED_MEMORY_TYPES[None]
    )



    sources = {


        "semantic":
        data["semantic"]["facts"],


        "episodic":
        data["episodic"]["events"],


        "emotional":
        data["emotional"]["states"],


        "relationship":
        data.get(
            "relationship_memory",
            []
        )

    }





    for memory_type, memories in sources.items():


        if memory_type not in allowed:

            continue



        for item in memories:


            score = calculate_score(
                message,
                item,
                memory_type,
                context
            )



            if score >=30:


                results.append({

                    "type":memory_type,

                    "memory":item,

                    "score":score

                })





    # =================================
    # REMOVE DUPLICATES
    # =================================


    unique = []

    seen = set()



    for item in results:


        content = item["memory"].get(
            "content",
            item["memory"].get(
                "trigger",
                ""
            )
        )


        if content not in seen:

            seen.add(content)

            unique.append(item)



    results = unique



    results.sort(
        key=lambda x:x["score"],
        reverse=True
    )





    # =================================
    # UPDATE RECALL
    # =================================


    for result in results[:1]:


        memory = result["memory"]


        memory["last_recalled"] = (
            datetime.now()
            .isoformat()
        )


        memory["recall_count"] = (
            memory.get(
                "recall_count",
                0
            )
            +
            1
        )



    save_memory(data)


    primary = []
    secondary = []


    for item in results:

        if item["score"] >= 100:

            primary.append(item)


        elif item["score"] >= 50:

            secondary.append(item)



    return {

        "primary": primary[:2],

        "secondary": secondary[:limit]

    }