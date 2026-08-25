class GoalDetector:
    """
    Detects learner goal from user message.
    """

    def detect(self, message):

        message = message.lower()

        # IELTS
        if "ielts" in message or "band" in message:
            return "ielts"

        # Academic
        if (
            "university" in message
            or "academic" in message
            or "study" in message
        ):
            return "academic"

        # Career
        if (
            "job" in message
            or "career" in message
            or "work" in message
        ):
            return "career"

        # Travel
        if (
            "travel" in message
            or "trip" in message
            ):
            return "travel"

        # Conversation
        if (
            "conversation" in message
            or "speaking" in message
            or "talk" in message
        ):
            return "conversation"

        return None