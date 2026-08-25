from core.memory import clear_memory, remember_fact
from core.memory_recall import recall_memory


clear_memory()


remember_fact(
    "I passed my physics exam",
    80,
    "achievement"
)


remember_fact(
    "I like mechanical engineering",
    70,
    "interest"
)


remember_fact(
    "I enjoy playing football",
    40,
    "hobby"
)


print("====================")
print("PHYSICS QUERY")
print("====================")

result = recall_memory(
    "I am worried about physics"
)

print(result)



print("\n====================")
print("ENGINEERING QUERY")
print("====================")

result = recall_memory(
    "I want to study engineering"
)

print(result)



print("\n====================")
print("RANDOM QUERY")
print("====================")

result = recall_memory(
    "I watched a movie today"
)

print(result)