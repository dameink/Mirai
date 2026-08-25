from core.analyzer import analyze_message



def test(message):

    print("\n====================")
    print("MESSAGE:")
    print(message)


    result = analyze_message(message)


    print("\nANALYSIS:")

    print(result)



# =====================
# TESTS
# =====================


test(
    "I am nervous before my university interview"
)


test(
    "Tell me about my goals"
)


test(
    "What projects am I working on?"
)


test(
    "Remember when I started Mirai?"
)


test(
    "What things do I like?"
)