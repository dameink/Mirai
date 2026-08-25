from core.emotion import change_emotion
from core.llm import ask_llm
from core.prompt import build_prompt
from core.memory import save_memory


def generate_response(
        message,
        context,
        strategy,
        voice
):

    message = message.strip()

    # Every interaction slightly changes Mirai
    change_emotion("energy", -1)
    change_emotion("curiosity", 1)


    # Simple memory detection
    if "my name is" in message.lower():

        name = message.lower().replace("my name is", "").strip()

        save_memory(
    {
        "content": f"User name is {name}",
        "category": "personal",
        "importance": 80
    }
)

        change_emotion("trust", 2)
        change_emotion("happiness", 3)


    # Build Mirai's context
    prompt = build_prompt(
        message,
        context,
        strategy,
        voice
    )


    # Ask LLM
    response = ask_llm(prompt)


    return response