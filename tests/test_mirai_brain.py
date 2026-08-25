from core.mirai_brain import think
import pprint



def test(message):

    print("\n====================")
    print("MESSAGE:")
    print(message)

    print("\nTHINKING...")

    result = think(
        message
    )

    print("\nBRAIN OUTPUT:")
    
    pprint.pp(
        result,
        width=120
    )



# =====================================
# TEST CASES
# =====================================


tests = [

    "I am nervous before my university interview",

    "Tell me about my goals",

    "What projects am I working on?",

    "Remember when I started Mirai?",

    "What things do I like?",

    "I finished my project and I feel proud",

]



for message in tests:

    test(message)