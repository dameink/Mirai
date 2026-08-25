from core.response_engine import choose_response_strategy
from core.response_engine import get_response_context



def test_response(message):

    print("\n====================")
    print("USER:")
    print(message)


    context = get_response_context(message)


    print("\n====================")
    print("CONTEXT")
    print("====================")

    print("Intent:",
          context["user_intent"])

    print("Relationship:",
          context["relationship_stage"])

    print("Closeness:",
          context["closeness"])

    print("Bond:",
          context["bond"])

    print("Humor:",
          context["humor"])



    strategy = choose_response_strategy(
        context
    )


    print("\n====================")
    print("STRATEGY")
    print("====================")


    for key, value in strategy.items():

        print(
            key,
            ":",
            value
        )





# ======================
# TEST CASES
# ======================


test_response(
    "I passed my physics exam"
)


test_response(
    "I am worried about my future"
)


test_response(
    "I like mechanical engineering"
)


test_response(
    "Thank you for helping me"
)