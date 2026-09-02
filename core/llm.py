from openai import OpenAI
from dotenv import load_dotenv

import os
import time


load_dotenv()


client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)


MODEL = "poolside/laguna-s-2.1:free"


# =========================================
# LLM
# =========================================

def ask_llm(
    system_prompt,
    conversation=None,
    user_message=None
):
    """
    Main LLM interface.

    Message structure:

        system
        previous user/assistant messages
        current user message

    LLM failures are handled gracefully so
    they do not crash the FastAPI worker.
    """

    conversation = conversation or []

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    # =====================================
    # PREVIOUS CONVERSATION
    # =====================================

    for item in conversation[-20:]:

        role = item.get("role")
        content = item.get("content", "")

        if role not in ("user", "assistant"):
            continue

        if not content:
            continue

        messages.append(
            {
                "role": role,
                "content": content
            }
        )

    # =====================================
    # CURRENT USER MESSAGE
    # =====================================

    if user_message:

        messages.append(
            {
                "role": "user",
                "content": user_message
            }
        )

    # =====================================
    # REQUEST
    # =====================================

    start = time.time()

    max_retries = 3

    for attempt in range(max_retries):

        try:

            response = client.chat.completions.create(
                model=MODEL,
                messages=messages
            )

            elapsed = time.time() - start

            print(
                "LLM MODEL:",
                MODEL
            )

            print(
                "LLM TIME:",
                elapsed,
                "seconds"
            )

            # =================================
            # VALIDATE RESPONSE
            # =================================

            if not response.choices:

                print(
                    "LLM ERROR: "
                    "empty choices"
                )

                return (
                    "Hmm... I couldn't get "
                    "a response right now."
                )

            content = (
                response
                .choices[0]
                .message
                .content
            )

            if not content:

                print(
                    "LLM ERROR: "
                    "empty response content"
                )

                return (
                    "Hmm... I couldn't get "
                    "a response right now."
                )

            return content

        # =====================================
        # RATE LIMIT
        # =====================================

        except Exception as error:

            print(
                f"LLM ERROR "
                f"(attempt {attempt + 1}/{max_retries}): "
                f"{error}"
            )

            if attempt < max_retries - 1:
                time.sleep(2)
                continue

            return (
                "Hmm... I'm having trouble connecting "
                "right now. Please try again in a moment."
            )

    # =====================================
    # FINAL FALLBACK
    # =====================================

    return (
        "Hmm... I can't connect "
        "right now. Try again in a moment."
    )