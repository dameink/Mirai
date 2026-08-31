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


def ask_llm(prompt):
    start = time.time()

    max_retries = 3

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    }
                ]
            )

            end = time.time()

            print("LLM MODEL:", MODEL)
            print("LLM TIME:", end - start, "seconds")

            return response.choices[0].message.content

        except Exception as error:
            error_text = str(error)

            if "429" not in error_text:
                raise

            print(
                f"LLM RATE LIMIT "
                f"(attempt {attempt + 1}/{max_retries})"
            )

            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                print("LLM RATE LIMIT: all retries failed")
                return "Hmm... I can't connect right now. Try again in a moment."