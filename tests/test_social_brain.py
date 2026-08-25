from core.social_brain import process_social_interaction


messages = [

    "You are amazing",

    "You are truly amazing",

    "Thank you Mirai",

    "Thank you so much Mirai, you really helped me",

    "I passed my physics exam"

]


for message in messages:

    print("\n====================")
    print("USER:")
    print(message)

    result = process_social_interaction(message)

    print("\nEVENT:")
    print(result["event"])

    print("\nEMOTION:")
    print(result["emotion"]["state"])

    print("\nRELATIONSHIP:")
    print(result["relationship"])

    print("\nBEHAVIOR:")
    print(result["behavior"])