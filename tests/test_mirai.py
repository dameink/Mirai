from core.mirai import chat


messages = [

    "I am nervous before my university interview",

    "Tell me about my goals",

    "I finished my project and I feel proud"

]


for msg in messages:


    print("\n================")
    print("USER:")
    print(msg)


    result = chat(
        msg
    )


    print("\nMIRAI:")

    print(
        result["response"]
    )


    print("\nDECISION:")
    print(
        result["decision"]
    )