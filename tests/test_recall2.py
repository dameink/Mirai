from core.memory_recall import recall_memory


def test(query):

    print("\n========================")
    print("QUERY:")
    print(query)

    results = recall_memory(query)


    print("\nRESULTS:")


    if not results:

        print("NO MEMORY FOUND")
        return


    for r in results:

        print("\nTYPE:", r["type"])

        print(
            "SCORE:",
            r["score"]
        )

        print(
            "MEMORY:"
        )

        print(
            r["memory"]
        )



# =========================
# BASIC TESTS
# =========================


test(
    "Tell me about my goals"
)


test(
    "What career do I want?"
)


test(
    "What projects am I working on?"
)


test(
    "What things do I like?"
)


test(
    "What achievements do I have?"
)


# =========================
# EMOTION TESTS
# =========================


test(
    "I am nervous before my university interview"
)


test(
    "I feel happy after finishing something"
)


# =========================
# MEMORY CONNECTION TESTS
# =========================


test(
    "Remember when I started Mirai?"
)


test(
    "What did I want to become before?"
)


# =========================
# SYNONYM TESTS
# =========================


test(
    "Tell me about my dreams"
)


test(
    "What applications am I building?"
)


test(
    "What hobbies do I enjoy?"
)