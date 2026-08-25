from core.memory_recall import recall_memory


def test(query):

    print("\n========================")
    print("QUERY:")
    print(query)

    results = recall_memory(query)

    print("\nRESULTS:")

    for r in results:

        print("\nTYPE:", r["type"])
        print("SCORE:", r["score"])
        print("MEMORY:")
        print(r["memory"])



# =========================
# TESTS
# =========================


test(
    "Tell me about my goals"
)


test(
    "What career do I want?"
)


test(
    "I am nervous before my interview"
)


test(
    "What projects am I working on?"
)


test(
    "What achievements do I have?"
)


test(
    "What things do I like?"
)


test(
    "Remember when I started Mirai?"
)