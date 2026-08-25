from openai import OpenAI
from dotenv import load_dotenv
import os


load_dotenv()


client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)


def ask_llm(prompt):

    import time

    start = time.time()

    response = client.chat.completions.create(
        model="poolside/laguna-s-2.1:free",
        messages=[
            {
                "role":"system",
                "content":prompt
            }
        ]
    )

    end = time.time()

    print(
        "LLM TIME:",
        end-start,
        "seconds"
    )

    return response.choices[0].message.content