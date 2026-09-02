from datetime import datetime, timezone
import re

from db.models import Memory, EmotionalMemory


TYPE_WEIGHT = {
    "semantic": 1.0,
    "episodic": 1.15,
    "emotional": 1.25,
    "relationship": 1.2,
}


SYNONYMS = {
    "career": [
        "goal",
        "future",
        "profession",
        "job",
        "dream",
        "ambition",
    ],
    "goal": [
        "want",
        "wants",
        "working",
        "work",
        "plan",
        "future",
        "dream",
        "aim",
        "target",
    ],
    "project": [
        "building",
        "creating",
        "application",
        "app",
        "working",
        "work",
        "developing",
        "coding",
        "programming",
    ],
    "achievement": [
        "passed",
        "success",
        "succeeded",
        "finished",
        "completed",
        "accomplished",
        "won",
    ],
    "interest": [
        "like",
        "likes",
        "love",
        "loves",
        "enjoy",
        "enjoys",
        "hobby",
        "favorite",
        "favourite",
        "passion",
    ],
    "emotion": [
        "feel",
        "feeling",
        "mood",
        "state",
    ],
    "started": [
        "began",
        "created",
        "initial",
        "first",
        "origin",
    ],
    "remember": [
        "recall",
        "before",
        "past",
        "previous",
    ],
}


# Words that are explicitly related by normal English morphology.
# This is intentionally small and conservative.
WORD_FAMILIES = {
    "banking": {"bank", "banker", "banking"},
    "banker": {"bank", "banker", "banking"},
    "bank": {"bank", "banker", "banking"},

    "investing": {"invest", "investing", "investment", "investor"},
    "investment": {"invest", "investing", "investment", "investor"},
    "investor": {"invest", "investing", "investment", "investor"},

    "working": {"work", "working", "worked"},
    "worked": {"work", "working", "worked"},
    "work": {"work", "working", "worked"},

    "planning": {"plan", "planning", "planned"},
    "planned": {"plan", "planning", "planned"},
    "plan": {"plan", "planning", "planned"},

    "learning": {"learn", "learning", "learned"},
    "learned": {"learn", "learning", "learned"},
    "learn": {"learn", "learning", "learned"},
}


ALLOWED_MEMORY_TYPES = {
    "goal": [
        "semantic",
        "episodic",
    ],
    "project": [
        "semantic",
        "episodic",
    ],
    "interest": [
        "semantic",
    ],
    "achievement": [
        "semantic",
        "episodic",
    ],
    "emotion": [
        "emotional",
        "episodic",
    ],
    None: [
        "semantic",
        "episodic",
        "emotional",
    ],
}


STOPWORDS = {
    # English
    "a", "an", "the",
    "i", "you", "your", "my", "me",
    "we", "us", "he", "she", "they",
    "is", "are", "was", "were",
    "be", "been", "being",
    "to", "of", "in", "on", "at",
    "by", "as", "it", "this", "that",
    "and", "or", "but", "with",
    "for", "about", "if", "so",

    # Russian
    "я", "ты", "вы", "мы", "он", "она",
    "они", "мой", "моя", "мои", "мне",
    "меня", "тебя", "твой", "твоя",
    "это", "этот", "эта", "эти",
    "и", "или", "но", "а",
    "в", "во", "на", "из", "к", "ко",
    "с", "со", "у", "о", "об",
    "по", "для", "как", "что",
    "же", "бы", "ли",
}


# ============================================
# TEXT NORMALIZATION
# ============================================

def normalize_text(text):
    if not text:
        return set()

    text = str(text).lower()

    text = re.sub(
        r"[^\w\s]",
        " ",
        text,
        flags=re.UNICODE,
    )

    return {
        word
        for word in text.split()
        if word and word not in STOPWORDS
    }


# ============================================
# WORD EXPANSION
# ============================================

def expand_words(words):
    expanded = set(words)

    for word in words:

        # Synonyms
        for key, values in SYNONYMS.items():

            if word == key:
                expanded.update(values)

            elif word in values:
                expanded.add(key)

        # Morphological families
        family = WORD_FAMILIES.get(word)

        if family:
            expanded.update(family)

    return expanded


# ============================================
# SIMILARITY
# ============================================

def similarity(message, content):
    message_words = normalize_text(message)
    content_words = normalize_text(content)

    if not message_words or not content_words:
        return 0

    message_expanded = expand_words(
        message_words
    )

    content_expanded = expand_words(
        content_words
    )

    common = (
        message_expanded
        & content_expanded
    )

    if not common:
        return 0

    denominator = min(
        len(message_expanded),
        len(content_expanded),
    )

    if denominator == 0:
        return 0

    return (
        len(common)
        / denominator
    ) * 100


# ============================================
# CONTEXT DETECTION
# ============================================

def detect_context(message):
    if not message:
        return None

    msg = str(message).lower()

    # ----------------------------------------
    # EMOTION
    # ----------------------------------------

    if any(
        x in msg
        for x in [
            "feel",
            "feeling",
            "nervous",
            "stress",
            "stressed",
            "sad",
            "happy",
            "afraid",
            "lonely",
            "worried",
            "anxious",

            "чувств",
            "нервни",
            "стресс",
            "груст",
            "счастлив",
            "боюсь",
            "одинок",
            "тревог",
            "пережива",
        ]
    ):
        return "emotion"

    # ----------------------------------------
    # ACHIEVEMENT
    # ----------------------------------------

    if any(
        x in msg
        for x in [
            "achievement",
            "success",
            "succeeded",
            "passed",
            "completed",
            "finished",
            "accomplished",
            "won",
            "managed to",

            "достиг",
            "успех",
            "сдал",
            "закончил",
            "завершил",
            "получил",
            "выиграл",
        ]
    ):
        return "achievement"

    # ----------------------------------------
    # PROJECT
    # ----------------------------------------

    if any(
        x in msg
        for x in [
            "project",
            "building",
            "creating",
            "application",
            "app",
            "developing",
            "coding",
            "programming",

            "проект",
            "создаю",
            "создал",
            "приложение",
            "разрабатываю",
            "разработка",
            "код",
            "программирую",
        ]
    ):
        return "project"

    # ----------------------------------------
    # GOAL
    # ----------------------------------------

    if any(
        x in msg
        for x in [
            "career",
            "profession",
            "job",
            "future",
            "ambition",
            "career goal",
            "life goal",
            "my goal",
            "my dream",
            "my plan",
            "i want",
            "i want to become",
            "i want to be",
            "i plan to",
            "i am planning to",
            "i hope to become",

            "карьер",
            "професси",
            "работ",
            "будущ",
            "амбици",
            "моя цель",
            "моя мечта",
            "мой план",
            "хочу",
            "хочу стать",
            "хочу быть",
            "планирую",
        ]
    ):
        return "goal"

    # ----------------------------------------
    # INTEREST
    # ----------------------------------------

    if any(
        x in msg
        for x in [
            "like",
            "love",
            "interest",
            "interested",
            "hobby",
            "enjoy",
            "favorite",
            "favourite",
            "passion",

            "нрав",
            "люблю",
            "интерес",
            "хобби",
            "увлека",
            "любим",
        ]
    ):
        return "interest"

    return None


# ============================================
# CATEGORY BONUS
# ============================================

def category_bonus(
    message,
    memory,
    context=None,
):
    if context is None:
        context = detect_context(message)

    category = memory.get(
        "category",
        "",
    )

    mapping = {
        "goal": {
            "goal": 80,
            "career": 80,
        },

        "project": {
            "project": 80,
        },

        "achievement": {
            "achievement": 70,
        },

        "interest": {
            "interest": 70,
        },

        "emotion": {
            "emotion": 80,
            "stress": 60,
        },
    }

    if category == "personal":

        msg = str(message).lower()

        content = str(
            memory.get(
                "content",
                "",
            )
        ).lower()

        if (
            "my name" in msg
            and "user name" in content
        ):
            return 80

    return mapping.get(
        context,
        {},
    ).get(
        category,
        0,
    )


# ============================================
# EMOTION BONUS
# ============================================

def emotion_bonus(
    message,
    memory,
    context=None,
):
    if context is None:
        context = detect_context(message)

    if context != "emotion":
        return 0

    msg = str(message).lower()

    emotion = memory.get(
        "emotion"
    )

    if emotion == "anxiety":

        if any(
            x in msg
            for x in [
                "nervous",
                "stress",
                "afraid",
                "anxious",
                "worried",

                "нервни",
                "стресс",
                "боюсь",
                "тревог",
                "пережива",
            ]
        ):
            return 80

    if emotion == "happiness":

        if any(
            x in msg
            for x in [
                "happy",
                "proud",
                "excited",

                "счастлив",
                "горжусь",
                "рад",
            ]
        ):
            return 70

    return 0


# ============================================
# RECENCY
# ============================================

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

        if date.tzinfo is None:
            date = date.replace(
                tzinfo=timezone.utc
            )

        now = datetime.now(
            timezone.utc
        )

        days = (
            now - date
        ).days

        return max(
            0,
            20 - days * 0.05,
        )

    except (
        ValueError,
        TypeError,
    ):
        return 5


# ============================================
# SCORE
# ============================================

def calculate_score(
    message,
    memory,
    memory_type=None,
    context=None,
):
    content = memory.get(
        "content",
        memory.get(
            "trigger",
            "",
        ),
    )

    lexical_similarity = similarity(
        message,
        content,
    )

    category_bonus_value = category_bonus(
        message,
        memory,
        context,
    )

    emotion_bonus_value = emotion_bonus(
        message,
        memory,
        context,
    )

    recency_value = recency(
        memory
    )

    # ----------------------------------------
    # HARD RELEVANCE GATE
    # ----------------------------------------

    if (
        lexical_similarity <= 0
        and category_bonus_value <= 0
    ):
        return 0

    score = (
        lexical_similarity * 0.4

        + memory.get(
            "importance",
            0,
        ) * 0.2

        + memory.get(
            "confidence",
            50,
        ) * 0.15

        + recency_value

        + category_bonus_value

        + emotion_bonus_value
    )

    memory_type = (
        memory_type
        or memory.get(
            "type",
            "semantic",
        )
    )

    score *= TYPE_WEIGHT.get(
        memory_type,
        1.0,
    )

    return score


# ============================================
# DB MEMORY CONVERTERS
# ============================================

def _memory_row_to_dict(row):
    return {
        "id": row.id,
        "type": row.memory_type,
        "content": row.content,
        "importance": row.importance,
        "category": row.category,
        "created": (
            row.created_at.isoformat()
            if row.created_at
            else None
        ),
        "last_recalled": (
            row.last_recalled.isoformat()
            if row.last_recalled
            else None
        ),
        "recall_count": row.recall_count or 0,
        "emotion": row.emotion,
        "confidence": row.confidence or 50,
    }


def _emotional_row_to_dict(row):
    return {
        "id": row.id,
        "type": "emotional",
        "emotion": row.emotion,
        "trigger": row.trigger,
        "intensity": row.intensity,
        "created": (
            row.created_at.isoformat()
            if row.created_at
            else None
        ),
    }


# ============================================
# RECALL MEMORY
# ============================================

def recall_memory(
    message,
    limit=5,
    cognition=None,
    user_id=None,
    db=None,
):
    """
    Recall memories relevant to the current message.

    Pipeline:

        user message
            ↓
        context detection
            ↓
        user-scoped DB memories
            ↓
        relevance scoring
            ↓
        hard relevance gate
            ↓
        ranking
            ↓
        primary / secondary
    """

    if db is None:
        raise ValueError(
            "db is required"
        )

    if not user_id:
        raise ValueError(
            "user_id is required"
        )

    # ----------------------------------------
    # CONTEXT
    # ----------------------------------------

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
        ALLOWED_MEMORY_TYPES[None],
    )

    # ----------------------------------------
    # LOAD USER-SCOPED DB DATA
    # ----------------------------------------

    semantic_rows = (
        db.query(Memory)
        .filter(
            Memory.user_id == user_id,
            Memory.memory_type == "semantic",
        )
        .all()
    )

    episodic_rows = (
        db.query(Memory)
        .filter(
            Memory.user_id == user_id,
            Memory.memory_type == "episodic",
        )
        .all()
    )

    emotional_rows = (
        db.query(EmotionalMemory)
        .filter(
            EmotionalMemory.user_id == user_id,
        )
        .all()
    )

    sources = {
        "semantic": [
            _memory_row_to_dict(row)
            for row in semantic_rows
        ],

        "episodic": [
            _memory_row_to_dict(row)
            for row in episodic_rows
        ],

        "emotional": [
            _emotional_row_to_dict(row)
            for row in emotional_rows
        ],
    }

    # ----------------------------------------
    # SCORE
    # ----------------------------------------

    results = []

    for memory_type, memories in sources.items():

        if memory_type not in allowed:
            continue

        for memory in memories:

            score = calculate_score(
                message,
                memory,
                memory_type,
                context,
            )

            if score >= 30:

                results.append(
                    {
                        "type": memory_type,
                        "memory": memory,
                        "score": score,
                    }
                )

    # ----------------------------------------
    # REMOVE DUPLICATES
    # ----------------------------------------

    unique = []
    seen = set()

    for item in results:

        memory = item["memory"]

        content = memory.get(
            "content",
            memory.get(
                "trigger",
                "",
            ),
        )

        normalized_content = (
            str(content)
            .strip()
            .lower()
        )

        if not normalized_content:
            continue

        if normalized_content in seen:
            continue

        seen.add(
            normalized_content
        )

        unique.append(item)

    results = unique

    # ----------------------------------------
    # SORT
    # ----------------------------------------

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    # ----------------------------------------
    # UPDATE RECALL METADATA
    # ----------------------------------------

    if results:

        primary_memory = (
            results[0]["memory"]
        )

        memory_id = (
            primary_memory.get("id")
        )

        if memory_id:

            if results[0]["type"] in {
                "semantic",
                "episodic",
            }:

                row = (
                    db.query(Memory)
                    .filter(
                        Memory.id == memory_id,
                        Memory.user_id == user_id,
                    )
                    .first()
                )

                if row:

                    row.last_recalled = (
                        datetime.now(
                            timezone.utc
                        )
                    )

                    row.recall_count = (
                        row.recall_count or 0
                    ) + 1

                    row.confidence = min(
                        100,
                        (row.confidence or 50)
                        + 5,
                    )

                    primary_memory[
                        "last_recalled"
                    ] = (
                        row.last_recalled.isoformat()
                    )

                    primary_memory[
                        "recall_count"
                    ] = row.recall_count

                    primary_memory[
                        "confidence"
                    ] = row.confidence

        db.commit()

    # ----------------------------------------
    # CLASSIFY
    # ----------------------------------------

    primary = []
    secondary = []

    for item in results:

        if item["score"] >= 100:
            primary.append(item)

        elif item["score"] >= 50:
            secondary.append(item)

    return {
        "primary": primary[:2],
        "secondary": secondary[:limit],
    }