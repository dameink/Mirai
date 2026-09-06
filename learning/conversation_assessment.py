from learning.evidence import Evidence


class ConversationAssessment:
    """
    Conservative assessment of ordinary English messages.

    This is not a full language model.
    It converts observable properties of a user's message
    into learning Evidence objects that can be processed
    by the existing SkillUpdateSystem.
    """

    def __init__(self, learner):
        self.learner = learner

    # =====================================================
    # MAIN ENTRY POINT
    # =====================================================

    def assess(self, message):
        """
        Assess an ordinary user message and return Evidence objects.

        The assessment is intentionally conservative:
        a short message produces limited evidence,
        while clearer/longer messages provide stronger evidence.
        """

        if not message:
            return []

        text = str(message).strip()

        if not text:
            return []

        # Do not assess messages that are clearly not English.
        if not self.is_likely_english(text):
            return []

        evidences = []

        fluency = self.assess_fluency(text)

        if fluency is not None:
            evidences.append(
                self.create_evidence(
                    category="speaking",
                    skill="fluency",
                    value=fluency["value"],
                    certainty=fluency["certainty"],
                    topic="conversation",
                    evidence_type="conversation",
                )
            )

        grammar = self.assess_grammar(text)

        for item in grammar:
            evidences.append(
                self.create_evidence(
                    category="grammar",
                    skill=item["skill"],
                    value=item["value"],
                    certainty=item["certainty"],
                    topic=item["topic"],
                    evidence_type="conversation",
                )
            )

        vocabulary = self.assess_vocabulary(text)

        if vocabulary is not None:
            evidences.append(
                self.create_evidence(
                    category="vocabulary",
                    skill="range",
                    value=vocabulary["value"],
                    certainty=vocabulary["certainty"],
                    topic="vocabulary range",
                    evidence_type="conversation",
                )
            )

        return evidences

    # =====================================================
    # ENGLISH DETECTION
    # =====================================================

    def is_likely_english(self, text):
        """
        Detect whether a message is likely English.

        The detector is intentionally permissive because this function
        is only a language gate. The actual assessment remains conservative.
        """

        words = self.tokenize(text)

        if not words:
            return False

        # Common English function words.
        english_words = {
            "a", "an", "the",
            "i", "me", "my", "mine",
            "you", "your", "yours",
            "he", "him", "his",
            "she", "her", "hers",
            "it", "its",
            "we", "us", "our", "ours",
            "they", "them", "their", "theirs",

            "am", "is", "are", "was", "were",
            "be", "been", "being",

            "have", "has", "had",
            "do", "does", "did",

            "will", "would",
            "can", "could",
            "should", "may", "might",
            "must",

            "want", "need", "like", "love",
            "think", "know", "understand",
            "go", "went", "going",
            "come", "came", "coming",
            "make", "made",
            "get", "got",
            "take", "took",
            "give", "gave",
            "see", "saw",
            "say", "said",
            "tell", "told",
            "feel", "felt",
            "look", "looked",
            "study", "studied", "studying",
            "learn", "learned", "learning",
            "work", "worked", "working",
            "live", "lived", "living",
            "try", "tried",
            "help", "helped",

            "good", "bad", "great",
            "happy", "sad", "tired",
            "fine", "okay", "ok",
            "today", "yesterday", "tomorrow",
            "now", "here", "there",

            "english", "university", "school",
            "student", "friend", "friends",
            "physics", "math", "chemistry",

            "and", "or", "but", "because",
            "so", "if", "with", "from",
            "for", "about", "of", "to",
            "in", "on", "at", "by",
            "as",

            "very", "really", "also",
            "not", "no", "yes",
            "what", "where", "when",
            "why", "how",
            "who", "which",
        }

        matches = sum(
            1 for word in words
            if word in english_words
        )

        # Very short messages:
        # one recognizable English word is enough.
        if len(words) <= 2:
            return matches >= 1

        # Normal messages:
        # two English words are enough.
        if matches >= 2:
            return True

        # English contractions such as I'm, you're, don't.
        contractions = (
            "i'm", "you're", "he's", "she's",
            "it's", "we're", "they're",
            "don't", "doesn't", "didn't",
            "can't", "couldn't", "won't",
            "wouldn't", "isn't", "aren't",
            "wasn't", "weren't",
            "haven't", "hasn't", "hadn't",
        )

        lower = text.lower()

        if any(
            contraction in lower
            for contraction in contractions
        ):
            return True

        return self.has_english_structure(text)

    # =====================================================
    # TOKENIZATION
    # =====================================================

    def tokenize(self, text):
        cleaned = ""

        for char in text.lower():
            if char.isalpha() or char == "'":
                cleaned += char
            else:
                cleaned += " "

        return [
            word
            for word in cleaned.split()
            if word
        ]

    # =====================================================
    # ENGLISH STRUCTURE
    # =====================================================

    def has_english_structure(self, text):
        lower = text.lower()

        subjects = (
            "i ",
            "you ",
            "he ",
            "she ",
            "we ",
            "they ",
            "it ",
        )

        verbs = (
            " am ",
            " is ",
            " are ",
            " was ",
            " were ",
            " have ",
            " has ",
            " had ",
            " do ",
            " does ",
            " did ",
            " want ",
            " need ",
            " like ",
            " think ",
            " went ",
            " go ",
            " study ",
            " learn ",
        )

        has_subject = lower.startswith(subjects)

        padded = " " + lower + " "

        has_verb = any(
            verb in padded
            for verb in verbs
        )

        return has_subject and has_verb

    # =====================================================
    # FLUENCY
    # =====================================================

    def assess_fluency(self, text):
        words = self.tokenize(text)

        word_count = len(words)

        if word_count == 0:
            return None

        # Very short messages provide very little evidence.
        if word_count <= 2:
            return {
                "value": 50,
                "certainty": 25,
            }

        if word_count <= 5:
            return {
                "value": 60,
                "certainty": 35,
            }

        if word_count <= 10:
            return {
                "value": 70,
                "certainty": 45,
            }

        if word_count <= 20:
            return {
                "value": 78,
                "certainty": 55,
            }

        return {
            "value": 82,
            "certainty": 60,
        }

    # =====================================================
    # GRAMMAR
    # =====================================================

    def assess_grammar(self, text):
        """
        Detect only a small number of high-confidence patterns.

        We deliberately avoid pretending to understand
        every possible English grammar construction.
        """

        lower = text.lower()
        results = []

        # -------------------------------------------------
        # Explicit known tense mistakes
        # -------------------------------------------------

        if "goed" in self.tokenize(text):
            results.append(
                {
                    "skill": "tenses",
                    "value": 35,
                    "certainty": 90,
                    "topic": "Past Simple",
                }
            )

        # -------------------------------------------------
        # Explicit known word-order / structure mistake
        # -------------------------------------------------

        if "i am agree" in lower:
            results.append(
                {
                    "skill": "word_order",
                    "value": 40,
                    "certainty": 85,
                    "topic": "sentence structure",
                }
            )

        # -------------------------------------------------
        # Basic past-tense evidence
        # -------------------------------------------------

        past_markers = (
            "yesterday",
            "last week",
            "last month",
            "last year",
            "ago",
            "was",
            "were",
            "went",
            "came",
            "did",
            "had",
            "got",
            "made",
            "saw",
            "said",
        )

        has_past_marker = any(
            marker in lower
            for marker in past_markers
        )

        if has_past_marker and "goed" not in self.tokenize(text):
            results.append(
                {
                    "skill": "tenses",
                    "value": 75,
                    "certainty": 45,
                    "topic": "Past Simple",
                }
            )

        # -------------------------------------------------
        # Basic sentence structure evidence
        # -------------------------------------------------

        if self.has_english_structure(text):
            results.append(
                {
                    "skill": "word_order",
                    "value": 75,
                    "certainty": 35,
                    "topic": "sentence structure",
                }
            )

        return results

    # =====================================================
    # VOCABULARY
    # =====================================================

    def assess_vocabulary(self, text):
        words = self.tokenize(text)

        if not words:
            return None

        unique_words = set(words)

        if len(words) <= 3:
            return {
                "value": 50,
                "certainty": 25,
            }

        lexical_diversity = len(unique_words) / len(words)

        if len(words) <= 6:
            base_value = 58
        elif len(words) <= 12:
            base_value = 68
        elif len(words) <= 20:
            base_value = 76
        else:
            base_value = 82

        # Slightly reward lexical variety.
        if lexical_diversity >= 0.85:
            base_value += 5
        elif lexical_diversity < 0.55:
            base_value -= 5

        base_value = max(
            0,
            min(100, base_value)
        )

        certainty = min(
            65,
            25 + len(words) * 2
        )

        return {
            "value": base_value,
            "certainty": certainty,
        }

    # =====================================================
    # EVIDENCE CREATION
    # =====================================================

    def create_evidence(
        self,
        category,
        skill,
        value,
        certainty,
        topic,
        evidence_type="conversation",
    ):
        return Evidence(
            skill=skill,
            category=category,
            value=value,
            topic=topic,
            evidence_type=evidence_type,
            source="conversation",
            certainty=certainty,
            context="conversation",
            difficulty=None,
        )