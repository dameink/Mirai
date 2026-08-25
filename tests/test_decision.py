from core.decision import make_decision



messages = [

"I am nervous before my university interview",

"Tell me about my goals",

"What projects am I working on?"

]


for message in messages:


    print("\n===================")

    print(message)


    result = make_decision(
        message
    )


    print(result)