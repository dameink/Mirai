from core.memory import remember_semantic, load_memory


remember_semantic(
    "I want to become a nuclear engineer",
    90,
    "goal"
)


remember_semantic(
    "I changed my mind, I want to become a mechanical engineer",
    90,
    "goal"
)


print(load_memory()["semantic"]["facts"])