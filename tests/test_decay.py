from core.memory_decay import (
    apply_memory_decay
)

from core.memory import get_memory



print("BEFORE")

print(
    get_memory()
)


apply_memory_decay()


print("\nAFTER")


print(
    get_memory()
)