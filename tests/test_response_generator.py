from core.response_engine import (
    get_response_context,
    choose_response_strategy
)

from core.response_generator import generate_response



message = "I passed my physics exam"



context = get_response_context(
    message
)


strategy = choose_response_strategy(
    context
)


response = generate_response(
    strategy,
    context
)


print("================")
print("STRATEGY")
print("================")

print(strategy)


print("================")
print("RESPONSE")
print("================")

print(response)