from core.mirai import chat


def main():
    print("Mirai CLI")
    print("Type /help for commands.")
    print("Type /exit to quit.\n")

    while True:
        try:
            message = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not message:
            continue

        if message.lower() in {"/exit", "/quit"}:
            print("Goodbye.")
            break

        if message.lower() == "/help":
            print("""
Commands:
/help        Show this help
/memory      Show memory
/status      Show Mirai state
/debug       Show debug information
/learning    Show learning state
/reset       Reset Mirai
/clear       Clear conversation
/forget      Forget memory
/exit        Exit
""")
            continue

        try:
            result = chat(message)

            if isinstance(result, dict):
                response = result.get("response", result)
            else:
                response = result

            print(f"Mirai: {response}")

        except Exception as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    main()