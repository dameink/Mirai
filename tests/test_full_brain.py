from core.social_brain import process_social_interaction
from core.memory import clear_memory
from core.relationship import reset_relationship
from core.emotion import get_emotion, reset_emotion
from core.relationship import get_relationship
from core.response_engine import get_response_context



# clean start

clear_memory()
reset_relationship()
reset_emotion()



messages = [

    "Hello Mirai",

    "I passed my physics exam",

    "I am worried about my future",

    "I like mechanical engineering"

]



for message in messages:


    print("\n====================")
    print("USER:")
    print(message)


    result = process_social_interaction(
        message
    )


    print("\nEVENT:")
    print(
        result["event"]
    )


    print("\nEMOTION:")
    print(
        get_emotion()["state"]
    )


    print("\nRELATIONSHIP:")
    print(
        get_relationship()
    )


    print("\nCONTEXT:")

    context = get_response_context(
        message
    )


    for key, value in context.items():

        print(
            key,
            ":",
            value
        )