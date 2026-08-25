from core.llm import ask_llm
from core.prompt import build_prompt


message = "Hello"

prompt = build_prompt(message)

response = ask_llm(prompt)


print(response)