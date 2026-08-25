from core.social_brain import process_social_interaction
from core.memory import get_memory, clear_memory



clear_memory()


print("START MEMORY")

print(
    get_memory()
)



print("\n--- ACHIEVEMENT ---")


process_social_interaction(
    "I passed my physics exam"
)



print("\nMEMORY AFTER:")

print(
    get_memory()
)



print("\n--- NORMAL MESSAGE ---")


process_social_interaction(
    "Today was sunny"
)



print("\nFINAL MEMORY:")

print(
    get_memory()
)