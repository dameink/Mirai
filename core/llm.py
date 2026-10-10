import logging
import os
from functools import lru_cache

from dotenv import load_dotenv
from openai import OpenAI, RateLimitError, APITimeoutError

load_dotenv()
logger = logging.getLogger(__name__)
MODEL = os.getenv("MIRAI_LLM_MODEL", "poolside/laguna-s-2.1:free")


class LLMUnavailableError(RuntimeError):
    def __init__(self, message, code="model_unavailable", retry_after=None):
        super().__init__(message)
        self.code = code
        self.retry_after = retry_after


@lru_cache(maxsize=1)
def get_client():
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise LLMUnavailableError("Language model is not configured")
    return OpenAI(
        api_key=key,
        base_url="https://openrouter.ai/api/v1",
        timeout=25.0,
        max_retries=0,
    )


def ask_llm(system_prompt, conversation=None, user_message=None):
    messages = [{"role": "system", "content": system_prompt}]
    for item in (conversation or [])[-20:]:
        if item.get("role") in {"user", "assistant"} and item.get("content"):
            messages.append({"role": item["role"], "content": item["content"]})
    if user_message:
        messages.append({"role": "user", "content": user_message})
    try:
        response = get_client().chat.completions.create(
            model=MODEL, messages=messages, max_tokens=1500,
        )
        content = response.choices[0].message.content if response.choices else None
        if not content or not content.strip():
            raise LLMUnavailableError("Empty model response")
        return content
    except RateLimitError as error:
        # Never log provider bodies: they can contain private prompts or credentials.
        logger.warning("Language model request failed (RateLimitError)")
        raise LLMUnavailableError(
            "Mirai\'s AI service has reached its request limit. Please try again later.",
            code="model_rate_limited", retry_after=60,
        ) from error
    except APITimeoutError as error:
        logger.warning("Language model request failed (APITimeoutError)")
        raise LLMUnavailableError("Mirai took too long to respond. Please retry.", code="model_timeout") from error
    except Exception as error:
        # Do not log provider payloads, credentials, or private conversations.
        logger.warning("Language model request failed (%s)", type(error).__name__)
        raise LLMUnavailableError("Mirai is temporarily unavailable. Please try again.") from error
