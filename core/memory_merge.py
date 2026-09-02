from datetime import datetime, timezone
import re


STOP_WORDS = {
    "user",
    "i",
    "me",
    "my",
    "mine",
    "is",
    "am",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "do",
    "does",
    "did",
    "dont",
    "don't",
    "not",
    "no",
    "longer",
    "changed",
    "anymore",
    "any",
    "the",
    "a",
    "an",
    "to",
    "of",
    "and",
    "or",
    "but",
    "for",
    "with",
    "in",
    "on",
    "at",
    "from",
    "that",
    "this",
    "it",
    "likes",
    "like",
    "liked",
    "love",
    "loves",
    "loved",
    "want",
    "wants",
    "wanted",
}


def _now():
    return datetime.now(timezone.utc).isoformat()


# ============================================
# TEXT NORMALIZATION
# ============================================

def normalize(text):
    if not text:
        return set()

    text = str(text).lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text,
    )

    return set(text.split())


# ============================================
# MEANINGFUL KEYWORDS
# ============================================

def meaningful_keywords(text):
    words = normalize(text)

    return {
        word
        for word in words
        if word not in STOP_WORDS
    }


# ============================================
# TEXT SIMILARITY
# ============================================

def similarity(a, b):
    a_words = normalize(a)
    b_words = normalize(b)

    if not a_words or not b_words:
        return 0

    return (
        len(a_words & b_words)
        / len(a_words | b_words)
    )


# ============================================
# TOPIC SIMILARITY
# ============================================

def topic_similarity(a, b):
    a_words = meaningful_keywords(a)
    b_words = meaningful_keywords(b)

    if not a_words or not b_words:
        return 0

    return (
        len(a_words & b_words)
        / len(a_words | b_words)
    )


# ============================================
# DUPLICATE
# ============================================

def is_duplicate(new_memory, old_memory):
    return (
        similarity(
            new_memory.get("content", ""),
            old_memory.get("content", ""),
        )
        > 0.6
    )


# ============================================
# CONFLICT
# ============================================

def is_conflict(new_memory, old_memory):
    """
    Conservative conflict detection.

    A conflict requires:
    1. Same category.
    2. Actual topic overlap.
    3. Sufficient topic similarity.

    Negative words alone can never create a conflict.
    """

    new_category = new_memory.get("category")
    old_category = old_memory.get("category")

    if (
        new_category
        and old_category
        and new_category != old_category
    ):
        return False

    new_text = new_memory.get("content", "")
    old_text = old_memory.get("content", "")

    if not new_text or not old_text:
        return False

    new_topics = meaningful_keywords(new_text)
    old_topics = meaningful_keywords(old_text)

    if not new_topics or not old_topics:
        return False

    overlap = new_topics & old_topics

    if not overlap:
        return False

    topic_score = topic_similarity(
        new_text,
        old_text,
    )

    if topic_score < 0.4:
        return False

    return True


# ============================================
# REINFORCE
# ============================================

def reinforce_memory(memory):
    memory["confidence"] = min(
        100,
        memory.get("confidence", 50) + 10,
    )

    memory["recall_count"] = (
        memory.get("recall_count", 0) + 1
    )

    memory["last_recalled"] = _now()

    return memory


# ============================================
# UPDATE
# ============================================

def update_memory(old, new):
    old["content"] = new.get(
        "content",
        old.get("content", ""),
    )

    old["importance"] = new.get(
        "importance",
        old.get("importance", 50),
    )

    old["category"] = new.get(
        "category",
        old.get("category", "general"),
    )

    old["emotion"] = new.get(
        "emotion",
        old.get("emotion"),
    )

    old["confidence"] = min(
        100,
        old.get("confidence", 50) + 15,
    )

    old["last_updated"] = _now()

    return old


# ============================================
# MAIN MERGE
# ============================================

def merge_memory(new_memory, memories):

    for old_memory in memories:

        # ------------------------------------
        # CONFLICT
        # ------------------------------------

        if is_conflict(
            new_memory,
            old_memory,
        ):
            updated = update_memory(
                old_memory,
                new_memory,
            )

            return {
                "action": "updated",
                "memory": updated,
            }

        # ------------------------------------
        # DUPLICATE
        # ------------------------------------

        if is_duplicate(
            new_memory,
            old_memory,
        ):
            reinforced = reinforce_memory(
                old_memory,
            )

            return {
                "action": "reinforced",
                "memory": reinforced,
            }

    # ----------------------------------------
    # NEW
    # ----------------------------------------

    memories.append(new_memory)

    return {
        "action": "created",
        "memory": new_memory,
    }