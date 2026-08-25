from core.response_engine import get_response_context
from core.response_rules import choose_response_strategy


message = "I passed my physics exam"


context = get_response_context(message)


strategy = choose_response_strategy(context)


print(strategy)