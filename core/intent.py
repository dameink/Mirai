INTENTS = {


    "celebrate": [

        "passed",
        "won",
        "finished",
        "completed",
        "achieved",
        "success"

    ],


    "seek_support": [

        "sad",
        "worried",
        "stressed",
        "afraid",
        "problem",
        "difficult",
        "hard"

    ],


    "deep_talk": [

        "future",
        "dream",
        "life",
        "feel",
        "think about"

    ],


    "ask_opinion": [

        "what do you think",
        "your opinion",
        "do you think"

    ],


    "casual_chat": [

        "hello",
        "hi",
        "hey",
        "what's up"

    ],


    "fun": [

        "joke",
        "funny",
        "play",
        "game"

    ]

}



def detect_intent(message):

    message = message.lower()


    for intent, keywords in INTENTS.items():

        for keyword in keywords:

            if keyword in message:

                return intent


    return "normal_conversation"